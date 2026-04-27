from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from typing import Optional
from pathlib import Path
from contextlib import asynccontextmanager

from sqlalchemy import select

from backend.core.config import settings
from backend.core.database import init_db, AsyncSessionLocal
from backend.utils.auth import get_current_user_optional, get_current_user
from backend.core.security import hash_password
from backend.models.user import User


async def create_default_admin():
    """Create default admin user if it doesn't exist."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.username == "admin"))
        admin = result.scalar_one_or_none()
        if not admin:
            admin = User(
                username="admin",
                hashed_password=hash_password("admin123"),
                is_admin=True
            )
            session.add(admin)
            await session.commit()
            print("Default admin created: username='admin', password='admin123'")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    await init_db()
    await create_default_admin()
    yield


# Initialize FastAPI app
app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

# Get the project root directory (parent of backend/)
BASE_DIR = Path(__file__).parent.parent

# Mount static files (CSS/JS) - pointing to frontend folder
app.mount("/static", StaticFiles(directory=BASE_DIR / "frontend" / "static"), name="static")

# Initialize Jinja2 templates - pointing to frontend folder
templates = Jinja2Templates(directory=BASE_DIR / "frontend" / "templates")


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


# Include routers (API implementations live in routers/)
from backend.routers.auth import router as auth_router
from backend.routers.tasks import router as tasks_router
from backend.routers.admin import router as admin_router

app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(admin_router)


# Simple template routes (server-rendered pages)
@app.get("/", response_class=RedirectResponse)
async def root():
    """Root path redirects to index (or login if not authenticated)."""
    return RedirectResponse(url="/index")


@app.get("/index", response_class=HTMLResponse)
async def dashboard(request: Request, username: Optional[str] = Depends(get_current_user_optional)):
    """Dashboard - requires authentication."""
    if not username:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("index.html", {"request": request, "username": username})


@app.get("/task", response_class=HTMLResponse)
async def task_page(request: Request, username: Optional[str] = Depends(get_current_user_optional)):
    """Task management page - requires authentication."""
    if not username:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("task.html", {"request": request, "username": username})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, username: Optional[str] = Depends(get_current_user_optional)):
    """Login page - redirect to index if already authenticated."""
    if username:
        return RedirectResponse(url="/index")
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, username: Optional[str] = Depends(get_current_user_optional)):
    """Register page - redirect to index if already authenticated."""
    if username:
        return RedirectResponse(url="/index")
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Admin dashboard - requires admin privileges."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return templates.TemplateResponse("admin.html", {"request": request, "user": current_user})
