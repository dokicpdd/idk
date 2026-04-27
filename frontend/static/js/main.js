/**
 * Main entry point for task management page
 * Initializes all functionality when DOM is ready
 */

document.addEventListener("DOMContentLoaded", () => {
  // Setup authentication (logout button)
  setupLogout();

  // Setup task creation form
  const form = $("#create-form");
  if (form) {
    form.addEventListener("submit", handleCreateTask);
  }

  // Setup filter buttons
  const refreshBtn = $("#refresh");
  const applyBtn = $("#apply-filters");
  
  if (refreshBtn) {
    refreshBtn.addEventListener("click", loadTasks);
  }
  
  if (applyBtn) {
    applyBtn.addEventListener("click", loadTasks);
  }

  // Initial load
  loadTasks();
});
