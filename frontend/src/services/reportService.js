export async function generateReport(domain) {
  const res = await fetch("/api/generate-report", {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify({ domain }),
  });
  if (!res.ok) throw new Error("Failed to fetch tenants");
  const data = await res.json()
  return data;
}