/**
 * Authentication functionality
 */

/**
 * Setup logout button handler
 */
function setupLogout() {
  const logoutBtn = $("#logout-btn");
  if (!logoutBtn) return;

  logoutBtn.addEventListener("click", async () => {
    try {
      await authApi.logout();
      window.location.href = "/login";
    } catch (e) {
      toast(e.message, "error");
    }
  });
}

/**
 * Check if user is authenticated
 * @returns {boolean}
 */
function isAuthenticated() {
  // Check for auth cookie
  return document.cookie.includes("token=");
}

/**
 * Redirect to login if not authenticated
 */
function requireAuth() {
  if (!isAuthenticated()) {
    window.location.href = "/login";
    return false;
  }
  return true;
}
