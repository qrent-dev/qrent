export async function getUserSubscriptions(token: string) {
  const res = await fetch(`http://${process.env.NEXT_PUBLIC_BACKEND_URL}/users/subscriptions`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const errorText = await res.json();
    throw new Error(`Failed to fetch subscriptions: ${res.status} - ${errorText}`);
  }
  return res.json();
}
