export async function request(path, {method = "GET", body, headers}) {
    const res = await fetch(path, {
        method,
        headers: {"Content-Type": "application/json", ...(headers || {}) },
        credentials: "include",
        body: body ? JSON.stringify(body) : undefined,
    });

    let data = null;
    try { data = await res.json(); } catch {}
    return { ok: res.ok, status: res.status, data}
}

export const login = ({ email, password }) =>
  request("/api/login", { method: "POST", body: { email, password } });

export const register = ({ email, password, confirmPassword, invite }) =>
  request("/api/register", { method: "POST", body: { email, password, confirmPassword, invite } });

export const logout = () =>
  request('/api/logout', {method: "POST"});