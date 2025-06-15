import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  try {
    // Extract query parameters from the incoming request URL
    const url = new URL(request.url);
    const queryParams = url.searchParams.toString();

    const backendUrl = `http://${process.env.NEXT_PUBLIC_BACKEND_URL}/properties/region-summary?${queryParams}`;

    const res = await fetch(backendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${process.env.API_TOKEN}`,
      },
    });

    if (!res.ok) {
      throw new Error(`API error: ${res.statusText}`);
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error(error);
    return NextResponse.json({ error: error.message || 'Unknown error' }, { status: 500 });
  }
}
