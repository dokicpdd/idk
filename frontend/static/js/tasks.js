/**
 * Task management functionality
 */

/**
 * Build query parameters from filter inputs
 * @returns {URLSearchParams}
 */
function getQueryParams() {
  const params = new URLSearchParams();

  const q = $("#q")?.value?.trim();
  if (q) params.set("q", q);

  const completed = $("#completed-filter")?.value;
  if (completed === "true") params.set("completed", "true");
  if (completed === "false") params.set("completed", "false");

  const priority = $("#priority-filter")?.value?.trim();
  if (priority !== "") params.set("priority", priority);

  const sort = $("#sort")?.value;
  if (sort) params.set("sort", sort);
  
  const order = $("#order")?.value;
  if (order) params.set("order", order);

  params.set("limit", "50");
  params.set("offset", "0");
  
  return params;
}

/**
 * Load tasks from API and render them
 */
async function loadTasks() {
  showStatus("Loading…");
  try {
    const params = getQueryParams();
    const data = await api(`?${params.toString()}`);
    // Backend returns array directly
    renderTasks(Array.isArray(data) ? data : (data?.tasks || []));
    showStatus("");
  } catch (e) {
    showStatus("");
    toast(e.message, "error");
  }
}

/**
 * Render tasks list to the DOM
 * @param {Array} tasks - Array of task objects
 */
function renderTasks(tasks) {
  const list = $("#task-list");
  const tpl = $("#task-template");
  list.innerHTML = "";

  if (!tasks || tasks.length === 0) {
    const empty = document.createElement("div");
    empty.className = "muted";
    empty.textContent = "No tasks yet. Add one above.";
    list.appendChild(empty);
    return;
  }

  for (const t of tasks) {
    const node = tpl.content.cloneNode(true);
    const item = node.querySelector(".task-item");
    item.dataset.id = t.id;

    const checkbox = node.querySelector(".checkbox");
    const content = node.querySelector(".task-content");
    const tagsEl = node.querySelector(".task-tags");
    const prioEl = node.querySelector(".task-priority");
    const dueEl = node.querySelector(".task-due");

    content.textContent = t.content ?? "";
    checkbox.checked = !!t.completed;
    item.classList.toggle("completed", !!t.completed);

    tagsEl.textContent = t.tags ? `Tags: ${t.tags}` : "";
    prioEl.textContent =
      t.priority === null || t.priority === undefined ? "" : `Priority: ${t.priority}`;
    dueEl.textContent = t.due_date ? `Due: ${toDateInputValue(t.due_date)}` : "";

    setupTaskEditor(node, t);
    setupTaskActions(node, t, checkbox);

    list.appendChild(node);
  }
}

/**
 * Setup editor functionality for a task
 * @param {DocumentFragment} node - Task DOM node
 * @param {object} t - Task data
 */
function setupTaskEditor(node, t) {
  const editBtn = node.querySelector(".edit-btn");
  const saveBtn = node.querySelector(".save-btn");
  const cancelBtn = node.querySelector(".cancel-btn");
  const editor = node.querySelector(".task-editor");

  const editorContent = node.querySelector(".editor-content");
  const editorTags = node.querySelector(".editor-tags");
  const editorPriority = node.querySelector(".editor-priority");
  const editorDue = node.querySelector(".editor-due");
  const editorCompleted = node.querySelector(".editor-completed");

  function enterEdit() {
    editor.style.display = "block";
    editBtn.style.display = "none";
    saveBtn.style.display = "inline-flex";
    cancelBtn.style.display = "inline-flex";

    editorContent.value = t.content ?? "";
    editorTags.value = t.tags ?? "";
    editorPriority.value = t.priority ?? "";
    editorDue.value = toDateInputValue(t.due_date);
    editorCompleted.checked = !!t.completed;
  }

  function exitEdit() {
    editor.style.display = "none";
    editBtn.style.display = "inline-flex";
    saveBtn.style.display = "none";
    cancelBtn.style.display = "none";
  }

  editBtn.addEventListener("click", enterEdit);
  cancelBtn.addEventListener("click", exitEdit);

  saveBtn.addEventListener("click", async () => {
    const contentVal = editorContent.value.trim();
    if (!contentVal) {
      toast("Task content cannot be empty", "error");
      return;
    }

    const payload = {
      content: contentVal,
      tags: editorTags.value.trim() || null,
      priority: editorPriority.value.trim() === "" ? null : Number(editorPriority.value),
      due_date: editorDue.value ? editorDue.value : null,
      completed: editorCompleted.checked,
    };

    saveBtn.disabled = true;
    try {
      await api(`/${t.id}`, { method: "PATCH", body: JSON.stringify(payload) });
      await loadTasks();
    } catch (e) {
      toast(e.message, "error");
    } finally {
      saveBtn.disabled = false;
      exitEdit();
    }
  });
}

/**
 * Setup task action buttons (checkbox, delete)
 * @param {DocumentFragment} node - Task DOM node
 * @param {object} t - Task data
 * @param {HTMLInputElement} checkbox - Checkbox element
 */
function setupTaskActions(node, t, checkbox) {
  const delBtn = node.querySelector(".delete-btn");
  const item = node.querySelector(".task-item");

  checkbox.addEventListener("change", async () => {
    checkbox.disabled = true;
    try {
      await api(`/${t.id}`, {
        method: "PATCH",
        body: JSON.stringify({ completed: checkbox.checked }),
      });
      item.classList.toggle("completed", checkbox.checked);
    } catch (e) {
      toast(e.message, "error");
      checkbox.checked = !checkbox.checked;
    } finally {
      checkbox.disabled = false;
    }
  });

  delBtn.addEventListener("click", async () => {
    if (!confirm("Delete this task?")) return;
    delBtn.disabled = true;
    try {
      await api(`/${t.id}`, { method: "DELETE" });
      await loadTasks();
    } catch (e) {
      toast(e.message, "error");
    } finally {
      delBtn.disabled = false;
    }
  });
}

/**
 * Handle create task form submission
 * @param {Event} ev - Submit event
 */
async function handleCreateTask(ev) {
  ev.preventDefault();

  const content = $("#content").value.trim();
  const tags = $("#tags").value.trim();
  const priorityRaw = $("#priority").value.trim();
  const due = $("#due_date").value;
  const completed = $("#completed").checked;

  if (!content) {
    toast("Please enter a task.", "error");
    return;
  }

  const payload = {
    content,
    tags: tags || null,
    priority: priorityRaw === "" ? null : Number(priorityRaw),
    due_date: due ? due : null,
    completed: !!completed,
  };

  const form = ev.target;
  const submitBtn = form.querySelector('button[type="submit"]');
  submitBtn.disabled = true;
  showStatus("Creating…");
  
  try {
    const res = await api("", { method: "POST", body: JSON.stringify(payload) });
    // Accept either { success: true, task: {...}} or a plain created object
    if ((res?.success && res.task) || (res && res.id)) {
      form.reset();
      await loadTasks();
    } else {
      throw new Error("Unexpected response from server");
    }
  } catch (e) {
    toast(e.message, "error");
  } finally {
    submitBtn.disabled = false;
    showStatus("");
  }
}
