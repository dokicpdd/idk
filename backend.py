from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from typing import List, Optional
from datetime import datetime

from models import Task, TaskCreate, TaskRead, TaskUpdate
from database import init_db, get_session

# Initialize FastAPI app
app = FastAPI()

# Mount static files (CSS/JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")


# Keep error responses consistent for the frontend.
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": {"message": exc.detail}},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "error": {"message": "Invalid request", "details": exc.errors()}},
    )


# Create DB tables on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Root endpoint: redirect to dashboard (/index)
@app.get("/")
async def root():
    return RedirectResponse(url="/index")

# Dashboard page (index.html) - pass tasks so templates can render them if needed
@app.get("/index", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Task management page (task.html)
@app.get("/task", response_class=HTMLResponse)
async def get_tasks(request: Request):
    return templates.TemplateResponse("task.html", {"request": request})


# Small helper for consistent serialization.
def serialize_task(task: Task) -> dict:
    return TaskRead.model_validate(task).model_dump()


# API: Get tasks with filtering/sorting/pagination
@app.get("/api/tasks")
async def get_tasks_api(
    session: Session = Depends(get_session),
    completed: Optional[bool] = None,
    priority: Optional[int] = None,
    q: Optional[str] = None,
    sort: str = "created_at",
    order: str = "desc",
    limit: int = 50,
    offset: int = 0,
):
    if limit < 1 or limit > 200:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 200")
    if offset < 0:
        raise HTTPException(status_code=400, detail="offset must be >= 0")

    sort_map = {
        "created_at": Task.created_at,
        "updated_at": Task.updated_at,
        "due_date": Task.due_date,
        "priority": Task.priority,
    }
    sort_col = sort_map.get(sort)
    if sort_col is None:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    if order not in ("asc", "desc"):
        raise HTTPException(status_code=400, detail="Invalid order value")
    sort_expr = sort_col.asc() if order == "asc" else sort_col.desc()

    conditions = []
    if completed is not None:
        conditions.append(Task.completed == completed)
    if priority is not None:
        conditions.append(Task.priority == priority)
    if q:
        qn = q.strip()
        if qn:
            pattern = f"%{qn}%"
            conditions.append(Task.content.ilike(pattern) | Task.tags.ilike(pattern))

    where_clause = and_(*conditions) if conditions else None

    base_stmt = select(Task)
    count_stmt = select(func.count()).select_from(Task)
    if where_clause is not None:
        base_stmt = base_stmt.where(where_clause)
        count_stmt = count_stmt.where(where_clause)

    total = session.execute(count_stmt).scalar_one()
    stmt = base_stmt.order_by(sort_expr).offset(offset).limit(limit)
    tasks = session.execute(stmt).scalars().all()

    return {"success": True, "tasks": [serialize_task(t) for t in tasks], "pagination": {"total": total, "limit": limit, "offset": offset}}

# API: Add a new task (JSON)
@app.post("/api/tasks", status_code=status.HTTP_201_CREATED)
async def add_task_api(task_in: TaskCreate, session: Session = Depends(get_session)):
    content = (task_in.content or "").strip()
    if not content:
        raise HTTPException(status_code=400, detail="Task content is required")
    tags = task_in.tags.strip() if task_in.tags else None

    if task_in.priority is not None:
        if task_in.priority < 0 or task_in.priority > 10:
            raise HTTPException(status_code=400, detail="priority must be between 0 and 10")

    normalized = content.casefold()
    existing = session.execute(
        select(Task.id).where(func.lower(Task.content) == normalized).limit(1)
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=400, detail="Task already exists")

    now = datetime.utcnow()
    db_task = Task(
        content=content,
        tags=tags,
        priority=task_in.priority,
        due_date=task_in.due_date,
        completed=bool(task_in.completed),
    )
    # Your existing SQLite DB may not have defaults for these fields,
    # so set them explicitly for new records.
    db_task.created_at = now
    db_task.updated_at = now
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return {"success": True, "task": serialize_task(db_task)}

# API: Update a task (PUT - full replace style)
@app.put("/api/tasks/{task_id}")
async def update_task_api(task_id: int, task_in: TaskCreate, session: Session = Depends(get_session)):
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    content = (task_in.content or "").strip()
    if not content:
        raise HTTPException(status_code=400, detail="Task content is required")

    db_task.content = content
    db_task.tags = task_in.tags.strip() if task_in.tags else None
    db_task.priority = task_in.priority
    db_task.due_date = task_in.due_date
    db_task.completed = bool(task_in.completed)
    db_task.updated_at = datetime.utcnow()
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return {"success": True, "task": serialize_task(db_task)}

@app.patch("/api/tasks/{task_id}")
async def patch_task_api(task_id: int, task_in: TaskUpdate, session: Session = Depends(get_session)):
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_in.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    if "content" in update_data:
        content = (update_data["content"] or "").strip()
        if not content:
            raise HTTPException(status_code=400, detail="Task content cannot be empty")
        update_data["content"] = content
    if "tags" in update_data:
        update_data["tags"] = update_data["tags"].strip() if update_data["tags"] else None
    if "priority" in update_data and update_data["priority"] is not None:
        if update_data["priority"] < 0 or update_data["priority"] > 10:
            raise HTTPException(status_code=400, detail="priority must be between 0 and 10")

    for key, value in update_data.items():
        setattr(db_task, key, value)

    db_task.updated_at = datetime.utcnow()
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return {"success": True, "task": serialize_task(db_task)}

# API: Delete a task by ID
@app.delete("/api/tasks/{task_id}")
async def delete_task_api(task_id: int, session: Session = Depends(get_session)):
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Invalid task ID")
    deleted = serialize_task(db_task)
    session.delete(db_task)
    session.commit()
    return {"success": True, "deleted_task": deleted}