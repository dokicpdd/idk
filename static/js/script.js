// Get DOM elements
const addBtn = document.getElementById('add');
const newTaskInput = document.getElementById('new-task');
const taskList = document.getElementById('list');

// Initialize tasks from backend (to sync front/backend)
let tasks = Array.from(document.querySelectorAll('#list li')).map(li => {
  // Extract task text (exclude delete button text)
  return li.childNodes[0].textContent.trim();
});

// Add Task Handler (replace prompts with input field)
addBtn.addEventListener('click', () => {
  const taskText = newTaskInput.value.trim();
  
  // Validate input
  if (!taskText) {
    alert('Please enter a task!');
    return;
  }

  // Avoid duplicates
  if (tasks.includes(taskText)) {
    alert('This task already exists!');
    newTaskInput.value = '';
    return;
  }

  // Add to tasks array
  tasks.push(taskText);
  
  // Render updated tasks (no duplicates!)
  renderTasks();
  
  // Clear input
  newTaskInput.value = '';
});

// Delete Task Handler (delegated for dynamic elements)
taskList.addEventListener('click', (e) => {
  if (e.target.classList.contains('delete-btn')) {
    const taskToDelete = e.target.dataset.task;
    
    // Filter out the deleted task
    tasks = tasks.filter(task => task !== taskToDelete);
    
    // Re-render tasks
    renderTasks();
  }
});

// Render Tasks (replace list instead of appending to avoid duplicates)
function renderTasks() {
  // Clear existing list
  taskList.innerHTML = '';
  
  // Add each task to the list
  tasks.forEach(task => {
    const li = document.createElement('li');
    
    // Task text
    const taskText = document.createTextNode(task);
    li.appendChild(taskText);
    
    // Delete button
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'delete-btn';
    deleteBtn.dataset.task = task;
    deleteBtn.textContent = 'Delete';
    li.appendChild(deleteBtn);
    
    // Add to list
    taskList.appendChild(li);
  });
}