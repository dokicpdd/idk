/**
 * Utility functions used across the application
 */

// DOM selector shorthand
function $(sel) {
  return document.querySelector(sel);
}

// Show status message
function showStatus(msg) {
  const el = $("#status");
  if (el) el.textContent = msg;
}

// Show toast notification
function toast(message, kind = "error") {
  const el = $("#toast");
  if (!el) return;
  el.style.display = "block";
  el.className = `toast ${kind}`;
  el.textContent = message;
  window.clearTimeout(toast._t);
  toast._t = window.setTimeout(() => {
    el.style.display = "none";
  }, 3000);
}

// Convert date to YYYY-MM-DD format for input
function toDateInputValue(value) {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "";
  return d.toISOString().slice(0, 10);
}
