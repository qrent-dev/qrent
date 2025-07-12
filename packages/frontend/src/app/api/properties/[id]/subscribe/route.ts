import { NextRequest, NextResponse } from 'next/server';

export async function PUT(req: NextRequest, { params }: { params: { id: string } }) {
  console.log(
    `🔔 API Route HIT: ${req.method} /api/properties/${params.id}/${req.method === 'PUT' ? 'subscribe' : 'unsubscribe'}`
  );

  const propertyId = params.id;
  const token = req.headers.get('Authorization');

  const res = await fetch(
    `http://${process.env.NEXT_PUBLIC_BACKEND_URL}/properties/${propertyId}/subscribe`,
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
