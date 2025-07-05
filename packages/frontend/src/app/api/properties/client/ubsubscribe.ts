import { NextResponse } from 'next/server';

export async function unsubscribeFromProperty(propertyId: number, token: string) {
  const res = await fetch(
    `http://${process.env.NEXT_PUBLIC_BACKEND_URL}/properties/${propertyId}/unsubscribe`,
    {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Unsubscribe failed: ${res.status} - ${errorText}`);
  }
  const data = await res.json();
  return NextResponse.json(data);
}
