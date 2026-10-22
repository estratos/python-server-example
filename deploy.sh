#!/usr/bin/env bash
#
# deploy.sh - instala las dependencias y arranca el servidor de ejemplo FastAPI.
#
# Uso:
#   ./deploy.sh [opciones de uvicorn]
#
# Variables de entorno:
#   HOST          Interfaz de escucha (por defecto: 0.0.0.0)
#   PORT          Puerto (por defecto: 8000)
#   PYTHON_BIN    Intérprete de Python 3 (por defecto: python3 o python)
#   VENV_DIR      Directorio del entorno virtual (por defecto: .venv)
#   SKIP_INSTALL  "1" para no instalar dependencias (por defecto: 0)

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
VENV_DIR="${VENV_DIR:-.venv}"
SKIP_INSTALL="${SKIP_INSTALL:-0}"

usage() {
  cat <<'EOF'
Uso: ./deploy.sh [opciones de uvicorn]

Crea el entorno virtual si no existe, instala requirements.txt y arranca el
servidor en http://HOST:PORT. Las opciones extra se pasan a uvicorn, por
ejemplo: ./deploy.sh --reload

Variables de entorno:
  HOST          Interfaz de escucha            (por defecto 0.0.0.0)
  PORT          Puerto                          (por defecto 8000)
  PYTHON_BIN    Intérprete de Python 3          (por defecto python3 o python)
  VENV_DIR      Directorio del entorno virtual  (por defecto .venv)
  SKIP_INSTALL  1 para omitir la instalación    (por defecto 0)

Ejemplos:
  ./deploy.sh                     # servidor en http://0.0.0.0:8000
  PORT=9000 ./deploy.sh           # escucha en el puerto 9000
  HOST=127.0.0.1 ./deploy.sh      # solo accesible desde localhost
  ./deploy.sh --reload            # recarga automática en desarrollo
EOF
}

log() { printf '==> %s\n' "$*"; }
die() { printf 'Error: %s\n' "$*" >&2; exit 1; }

for arg in "$@"; do
  case "$arg" in
    -h | --help)
      usage
      exit 0
      ;;
  esac
done

find_python() {
  if [[ -n "${PYTHON_BIN:-}" ]]; then
    command -v "$PYTHON_BIN" >/dev/null 2>&1 ||
      die "PYTHON_BIN='$PYTHON_BIN' no es un ejecutable válido."
    printf '%s\n' "$PYTHON_BIN"
  elif command -v python3 >/dev/null 2>&1; then
    printf 'python3\n'
  elif command -v python >/dev/null 2>&1; then
    printf 'python\n'
  else
    die "no se encontró Python 3. Instálalo y vuelve a ejecutar el script."
  fi
}

find_venv_python() {
  if [[ -x "$VENV_DIR/bin/python" ]]; then
    printf '%s\n' "$VENV_DIR/bin/python"
  elif [[ -x "$VENV_DIR/Scripts/python.exe" ]]; then
    printf '%s\n' "$VENV_DIR/Scripts/python.exe"
  fi
}

PYTHON="$(find_python)"

"$PYTHON" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' ||
  die "se requiere Python 3.10 o superior (encontrado: $("$PYTHON" -V 2>&1))"

VENV_PYTHON="$(find_venv_python || true)"

if [[ -z "$VENV_PYTHON" ]]; then
  log "Creando entorno virtual en $VENV_DIR"
  "$PYTHON" -m venv "$VENV_DIR" || die "no se pudo crear el entorno virtual."
  VENV_PYTHON="$(find_venv_python || true)"
  [[ -n "$VENV_PYTHON" ]] || die "el entorno virtual no contiene un intérprete válido."
fi

if [[ "$SKIP_INSTALL" != "1" ]]; then
  log "Instalando dependencias"
  "$VENV_PYTHON" -m pip install --quiet --upgrade pip
  "$VENV_PYTHON" -m pip install --quiet -r requirements.txt
else
  log "SKIP_INSTALL=1: se omiten las dependencias"
fi

if [[ "$HOST" == "0.0.0.0" || "$HOST" == "::" ]]; then
  log "Arrancando servidor en http://127.0.0.1:$PORT (escucha en $HOST)"
else
  log "Arrancando servidor en http://$HOST:$PORT"
fi

exec "$VENV_PYTHON" -m uvicorn main:app --host "$HOST" --port "$PORT" "$@"
