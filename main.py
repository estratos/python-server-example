"""Servidor web de ejemplo con FastAPI.

Poner en marcha:
    uvicorn main:app --reload

Documentación interactiva de la API: http://127.0.0.1:8000/docs
"""

from __future__ import annotations

from itertools import count
from pathlib import Path
from string import Template

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Tareas API",
    description="Servidor web de ejemplo con FastAPI y almacenamiento en memoria.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Plantilla HTML de la biblioteca estándar: no hace falta instalar Jinja2.
_index_template = Template(
    (BASE_DIR / "templates" / "index.html").read_text(encoding="utf-8")
)


# --- Modelos -------------------------------------------------------------


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120, examples=["Comprar café"])
    done: bool = False


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    done: bool | None = None


class Task(TaskCreate):
    id: int


# --- Almacenamiento en memoria -------------------------------------------


_next_id = count(1)
_tasks: dict[int, Task] = {}


def create_task(title: str, done: bool = False) -> Task:
    task = Task(id=next(_next_id), title=title, done=done)
    _tasks[task.id] = task
    return task


def get_task_or_404(task_id: int) -> Task:
    task = _tasks.get(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada"
        )
    return task


for _title in ("Revisar el README", "Probar GET /api/tasks"):
    create_task(_title)


# --- Rutas ---------------------------------------------------------------


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index() -> HTMLResponse:
    return HTMLResponse(_index_template.substitute(task_count=len(_tasks)))


@app.get("/api/health", tags=["sistema"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/tasks", response_model=list[Task], tags=["tareas"])
async def list_tasks() -> list[Task]:
    return list(_tasks.values())


@app.post(
    "/api/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    tags=["tareas"],
)
async def add_task(payload: TaskCreate) -> Task:
    return create_task(payload.title, payload.done)


@app.patch("/api/tasks/{task_id}", response_model=Task, tags=["tareas"])
async def edit_task(task_id: int, payload: TaskUpdate) -> Task:
    task = get_task_or_404(task_id)
    updated = task.model_copy(update=payload.model_dump(exclude_none=True))
    _tasks[task_id] = updated
    return updated


@app.delete(
    "/api/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["tareas"],
)
async def remove_task(task_id: int) -> None:
    get_task_or_404(task_id)
    del _tasks[task_id]
