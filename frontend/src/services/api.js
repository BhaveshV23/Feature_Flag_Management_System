const API_BASE_URL = "/api";

export async function login(username, password) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const result = await response.json();

  if (!response.ok) {
    throw new Error(result.detail || "Unable to sign in.");
  }

  return result;
}
