from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# Initialize FastAPI app
app = FastAPI()

# Mount static files (CSS) - same as Flask's static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Jinja2 templates (same as Flask's templates folder)
templates = Jinja2Templates(directory="templates")

# In-memory task list (same as your original Flask code)
tasks = ["Buy groceries", "Finish homework"]  # Sample initial tasks


# Root endpoint: redirect to /task (same as Flask)
@app.get("/", response_class=RedirectResponse)
async def root():
    return RedirectResponse(url="/task")

# Task page: render HTML with tasks (same as Flask's /task)
@app.get("/task", response_class=HTMLResponse)
async def get_tasks(request: Request):
    # Pass tasks to the template (same as Flask's render_template)
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "list": tasks}  # "list" matches your HTML template variable
    )

# Optional: API endpoint to get tasks (JSON) - FastAPI bonus (not in Flask)
@app.get("/api/tasks")
async def get_tasks_api():
    return {"tasks": tasks}

# Optional: API endpoint to add a task (JSON) - FastAPI bonus
@app.post("/api/add-task")
async def add_task_api(task: str):
    if task and task not in tasks:
        tasks.append(task)
        return {"success": True, "tasks": tasks}
    return {"success": False, "message": "Task is empty or already exists"}

# Optional: API endpoint to delete a task (JSON) - FastAPI bonus
@app.delete("/api/delete-task/{task_id}")
async def delete_task_api(task_id: int):
    if 0 <= task_id < len(tasks):
        deleted_task = tasks.pop(task_id)
        return {"success": True, "deleted_task": deleted_task, "tasks": tasks}
    return {"success": False, "message": "Invalid task ID"}