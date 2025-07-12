import { NextRequest, NextResponse } from 'next/server';

export async function PUT(req: NextRequest, { params }: { params: { id: string } }) {
  const { id } = await params;
  const token = req.headers.get('Authorization');

  const res = await fetch(
    `http://${process.env.NEXT_PUBLIC_BACKEND_URL}/properties/${id}/subscribe`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: token || '',
      },
    }
  );

  if (!res.ok) {
    const errorText = await res.json();
    return NextResponse.json({ error: errorText }, { status: res.status });
  }

  const data = await res.json();
  return NextResponse.json(data);
}
