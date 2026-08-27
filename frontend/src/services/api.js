const API_BASE_URL = "/api";
const TOKEN_KEY = "flagflow_access_token";

async function parseResponse(response) {
  const responseText = await response.text();
  let result = null;

  if (responseText) {
    try {
      result = JSON.parse(responseText);
    } catch {
      result = { detail: responseText };
    }
  }

  if (!response.ok) {
    const error = new Error(result?.detail || result?.message || `Request failed with status ${response.status}`);
    error.status = response.status;
    error.response = result;
    throw error;
  }

  return result;
}

export async function authenticatedRequest(path, options = {}) {
  const token = localStorage.getItem(TOKEN_KEY);

  if (!token) {
    const error = new Error("Authentication token is missing.");
    error.status = 401;
    throw error;
  }

  const headers = new Headers(options.headers || {});
  headers.set("Authorization", `Bearer ${token}`);

  if (options.body !== undefined && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const body = options.body !== undefined && typeof options.body !== "string" && !(options.body instanceof FormData)
    ? JSON.stringify(options.body)
    : options.body;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    body,
  });

  return parseResponse(response);
}

export async function login(username, password) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  return parseResponse(response);
}

export function getFlags() {
  return authenticatedRequest("/flags");
}

export function getFlag(flagId) {
  return authenticatedRequest(`/flags/${flagId}`);
}

export function createFlag(flagData) {
  return authenticatedRequest("/flags", {
    method: "POST",
    body: flagData,
  });
}

export function updateFlag(flagId, flagData) {
  return authenticatedRequest(`/flags/${flagId}`, {
    method: "PUT",
    body: flagData,
  });
}

export function deleteFlag(flagId) {
  return authenticatedRequest(`/flags/${flagId}`, {
    method: "DELETE",
  });
}

export function getEnvironments() {
  return authenticatedRequest("/environment");
}

export function getEnvironment(environmentId) {
  return authenticatedRequest(`/environment/${environmentId}`);
}

export function createEnvironment(environmentData) {
  return authenticatedRequest("/environment", { method: "POST", body: environmentData });
}

export function updateEnvironment(environmentId, environmentData) {
  return authenticatedRequest(`/environment/${environmentId}`, { method: "PUT", body: environmentData });
}

export function deleteEnvironment(environmentId) {
  return authenticatedRequest(`/environment/${environmentId}`, { method: "DELETE" });
}

export function getTargetingRules() {
  return authenticatedRequest("/targeting-rules");
}

export function getTargetingRule(ruleId) {
  return authenticatedRequest(`/targeting-rules/${ruleId}`);
}

export function createTargetingRule(ruleData) {
  return authenticatedRequest("/targeting-rules", { method: "POST", body: ruleData });
}

export function updateTargetingRule(ruleId, ruleData) {
  return authenticatedRequest(`/targeting-rules/${ruleId}`, { method: "PUT", body: ruleData });
}

export function deleteTargetingRule(ruleId) {
  return authenticatedRequest(`/targeting-rules/${ruleId}`, { method: "DELETE" });
}
