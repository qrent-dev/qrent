import { NextResponse } from 'next/server';

export async function subscribeToProperty(propertyId: number, token: string) {
  const res = await fetch(
    `http://${process.env.NEXT_PUBLIC_BACKEND_URL}/properties/${propertyId}/subscribe`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!res.ok) {
    const errorText = await res.json();
    throw new Error(`Failed: ${res.status} - ${errorText}`);
  }

  const data = await res.json();
  return NextResponse.json(data);
}
