/**
 * API client for backend communication
 */

const API_BASE = "/api/tasks";

/**
 * Make API request to the backend
 * @param {string} path - API path (without base)
 * @param {object} options - Fetch options
 * @returns {Promise<any>} Response data
 */
async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });

  let payload = null;
  try {
    payload = await res.json();
  } catch (_) {
    // ignore JSON parse errors
  }

  if (!res.ok) {
    const msg = payload?.error?.message || payload?.detail || payload?.message || `Request failed (${res.status})`;
    throw new Error(msg);
  }

  return payload;
}

/**
 * Authentication API calls
 */
const authApi = {
  async logout() {
    const res = await fetch("/auth/logout", { method: "POST" });
    if (!res.ok) {
      throw new Error("Logout failed");
    }
    return res.json();
  }
};
