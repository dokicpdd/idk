# Task management (FastAPI)

 backend helping u manage ur task built with FastAPI + SQLAlchemy (async). This README explains how the project is organized, how requests flow, and how to run and test the app locally.

## Features
- User registration and simple signed-cookie session login (itsdangerous).
- Per-user tasks with CRUD (create / read / update / delete).
- Server-rendered pages (Jinja2 templates) for minimal UI: `/login`, `/register`, `/task`, `/index`.
- API routes are separated into routers (clean code organization).
- SQLite for storage (local `tasks.db`), DB tables created at startup.
- Basic tests + CI workflow scaffolded.

## Quick start (development)
1. Create a virtualenv and activate it (macOS / Linux):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   # or: pip install -e .   (if using pyproject.toml / editable install)
   ```
3. Run the app:
   ```bash
   python -m uvicorn backend.backend:app --reload
   ```
4. Open the browser: http://127.0.0.1:8000/login


## Project layout (important files)
- `backend/` - main python package
  - `backend/app.py` - FastAPI app entrypoint (registers routers, templates)
  - `backend/core/` - core helpers (database, config, security)
  - `backend/models.py` - SQLAlchemy ORM models and Pydantic schemas
  - `backend/routers/` - API routers (auth.py, tasks.py, admin.py)
  - `backend/utils/auth.py` - auth dependencies (get_current_user)
- `frontend/` - optional static/templates (served by app)
- `requirements.txt` - Python dependencies
- `Dockerfile` - container image (simple uvicorn run)
- `tests/` - pytest tests


## Request flow (login + API)
1. Browser GET `/login` → server returns `login.html`.
2. Browser POST `/auth/login` (JSON) → `routers/auth.login` checks user, sets signed cookie `token`.
3. Subsequent requests include cookie. Protected API routes use dependency `get_current_user`:
   - `get_current_user` reads cookie, verifies signature, loads `User` from DB.
   - If not authenticated, endpoints return 401.
4. Task endpoints live under `/api/tasks` and perform per-user CRUD.


## Tests
- Run tests with `pytest`.
- A basic test suite is in `backend/tests/test_api.py` that covers page redirects, register/login, and CRUD flows.


## Docker
- Build: `docker build -t todo-app .`
- Run: `docker run -p 8000:8000 todo-app`


## Notes and next steps
- SECRET key: set `SECRET_KEY` env var in production.
- For production use consider: HTTPS, secure cookie flags, CSRF protection, Alembic migrations.
- If you prefer API-only, remove templates and rely on the OpenAPI docs at `/docs`.


Tell me which of the above you'd like next.

