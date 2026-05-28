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

// Show toast notification with improved animations
function toast(message, kind = "error") {
  const el = $("#toast");
  if (!el) return;
  
  // Hide first if already showing
  if (el.style.display === "block") {
    el.style.opacity = "0";
    el.style.transform = "translateX(-50%) translateY(100px)";
    
    setTimeout(() => {
      showToast(el, message, kind);
    }, 300);
  } else {
    showToast(el, message, kind);
  }
}

function showToast(el, message, kind) {
  el.style.display = "block";
  el.className = `toast ${kind}`;
  el.textContent = message;
  
  // Trigger reflow
  el.offsetHeight;
  
  // Animate in
  el.style.opacity = "1";
  el.style.transform = "translateX(-50%) translateY(0)";
  
  window.clearTimeout(toast._t);
  toast._t = window.setTimeout(() => {
    // Animate out
    el.style.opacity = "0";
    el.style.transform = "translateX(-50%) translateY(100px)";
    
    setTimeout(() => {
      el.style.display = "none";
    }, 400);
  }, 3000);
}

// Convert date to YYYY-MM-DD format for input
function toDateInputValue(value) {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "";
  return d.toISOString().slice(0, 10);
}
