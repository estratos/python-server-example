# Servidor web de ejemplo con FastAPI

Aplicación pequeña y completa: API JSON + página HTML, datos en memoria, validación con
Pydantic, documentación automática con Swagger UI y tests.

## Requisitos

- Python 3.10 o superior (probado con 3.14)

## Instalación

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Ejecución

```powershell
uvicorn main:app --reload
```

Abre <http://127.0.0.1:8000>:

- `/` — interfaz web para gestionar tareas
- `/docs` — Swagger UI con la API interactiva
- `/redoc` — documentación alternativa en ReDoc

## Endpoints

| Método   | Ruta               | Descripción                                  |
| -------- | ------------------ | -------------------------------------------- |
| `GET`    | `/`                | Página HTML de ejemplo                       |
| `GET`    | `/api/health`      | Comprobación de estado (`{"status": "ok"}`)  |
| `GET`    | `/api/tasks`       | Lista todas las tareas                       |
| `POST`   | `/api/tasks`       | Crea una tarea → `201`                       |
| `PATCH`  | `/api/tasks/{id}`  | Actualiza `title` y/o `done`                 |
| `DELETE` | `/api/tasks/{id}`  | Elimina una tarea → `204`                    |

Ejemplos con `curl`:

```powershell
curl.exe http://127.0.0.1:8000/api/tasks
curl.exe -X POST http://127.0.0.1:8000/api/tasks -H "Content-Type: application/json" -d '{\"title\":\"Mi primera tarea\"}'
curl.exe -X PATCH http://127.0.0.1:8000/api/tasks/1 -H "Content-Type: application/json" -d '{\"done\":true}'
curl.exe -X DELETE http://127.0.0.1:8000/api/tasks/1
```

Los datos viven en un diccionario en memoria: se reinician al reiniciar el servidor.
Para producción, sustituye ese almacenamiento por una base de datos (por ejemplo SQLModel
o SQLAlchemy).

## Tests

```powershell
pip install -r requirements-dev.txt
python -m pytest
```

## Estructura

```
main.py                  Aplicación FastAPI (modelos, rutas, estado)
templates/index.html     Plantilla Jinja2 de la página principal
static/app.js            Lógica del cliente (fetch a la API)
static/style.css         Estilos (con modo claro/oscuro automático)
tests/test_main.py       Tests con TestClient
requirements.txt         Dependencias de ejecución
requirements-dev.txt     Dependencias de desarrollo (pytest, httpx)
```
