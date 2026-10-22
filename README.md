# Servidor web de ejemplo con FastAPI

Aplicación pequeña y completa: API JSON + página HTML, datos en memoria, validación con
Pydantic, documentación automática con Swagger UI y pruebas con la biblioteca estándar.

## Requisitos

- Python 3.10 o superior (probado con 3.14)
- Solo dos dependencias: `fastapi` y `uvicorn`

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

## Despliegue rápido con `deploy.sh`

El script crea el entorno virtual si no existe, instala `requirements.txt` y arranca
Uvicorn (Linux, macOS, WSL o Git Bash):

```bash
chmod +x deploy.sh
./deploy.sh                  # http://0.0.0.0:8000
PORT=9000 ./deploy.sh        # otro puerto
HOST=127.0.0.1 ./deploy.sh   # solo localhost
./deploy.sh --reload         # desarrollo con recarga automática
./deploy.sh --help           # ayuda
```

Variables de entorno: `HOST`, `PORT`, `PYTHON_BIN`, `VENV_DIR` y `SKIP_INSTALL=1`
(omite la instalación de dependencias). Cualquier argumento adicional se pasa a
`uvicorn`, por ejemplo `--workers 4`.

Desde PowerShell en Windows, invócalo a través de Git Bash:

```powershell
& "C:\Program Files\Git\bin\bash.exe" deploy.sh
```

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
python -m unittest discover -s tests -v
```

Las pruebas arrancan un servidor Uvicorn en el puerto `8765` y ejercitan la API real con
`urllib`, sin dependencias adicionales.

## Estructura

```
main.py                  Aplicación FastAPI (modelos, rutas, estado)
templates/index.html     HTML de la página principal (plantilla string.Template)
static/app.js            Lógica del cliente (fetch a la API)
static/style.css         Estilos (con modo claro/oscuro automático)
tests/test_api.py        Pruebas de humo con unittest + urllib
deploy.sh                Instala dependencias y arranca el servidor
requirements.txt         Dependencias (fastapi, uvicorn)
```

## Notas de diseño

- **Validación**: Pydantic rechaza títulos vacíos con `422` y limita la longitud a 120
  caracteres.
- **Sin Jinja2**: la página usa `string.Template` de la biblioteca estándar, así que el
  ejemplo se ejecuta con únicamente FastAPI y Uvicorn.
- **Sin XSS**: el cliente crea los nodos con `textContent`, no con `innerHTML`.
- **Estado en memoria**: suficiente para un ejemplo; no persistente ni seguro para
  múltiples procesos.
