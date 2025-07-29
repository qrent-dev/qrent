// @ts-nocheck
import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  const token = req.headers.get('Authorization');
  try {
    const res = await fetch(`http://${process.env.NEXT_PUBLIC_BACKEND_URL}/users/subscriptions`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: token || '',
      },
    });

    if (!res.ok) {
      const errorText = await res.json();
      throw new Error(`Failed to fetch subscriptions: ${res.status} - ${errorText}`);
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
