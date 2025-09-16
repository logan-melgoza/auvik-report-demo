export async function getTenants() {
  const res = await fetch("/api/tenants");
  if (!res.ok) throw new Error("Failed to fetch tenants");
  return res.json();
}
