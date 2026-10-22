"""Pruebas de humo de la API usando solo la biblioteca estándar.

Ejecutar desde la raíz del proyecto:
    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import threading
import time
import unittest
import urllib.error
import urllib.request

import uvicorn

import main

HOST = "127.0.0.1"
PORT = 8765
BASE_URL = f"http://{HOST}:{PORT}"


def request(
    method: str, path: str, payload: dict[str, object] | None = None
) -> tuple[int, object]:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        BASE_URL + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if data else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            body = response.read()
            return response.status, json.loads(body) if body else None
    except urllib.error.HTTPError as error:
        with error:
            body = error.read()
            return error.code, json.loads(body) if body else None


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        config = uvicorn.Config(main.app, host=HOST, port=PORT, log_level="warning")
        cls.server = uvicorn.Server(config)
        cls.thread = threading.Thread(target=cls.server.run, daemon=True)
        cls.thread.start()

        deadline = time.time() + 10
        while not cls.server.started:
            if time.time() > deadline:
                raise RuntimeError("El servidor de pruebas no arrancó")
            time.sleep(0.05)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.should_exit = True
        cls.thread.join(timeout=5)

    def test_health(self) -> None:
        status, body = request("GET", "/api/health")
        self.assertEqual(status, 200)
        self.assertEqual(body, {"status": "ok"})

    def test_index_renders_html(self) -> None:
        with urllib.request.urlopen(BASE_URL + "/", timeout=5) as response:
            html = response.read().decode()
            self.assertEqual(response.status, 200)
            self.assertIn("text/html", response.headers["Content-Type"])
        self.assertIn("<h1>Tareas</h1>", html)

    def test_list_has_seed_tasks(self) -> None:
        status, body = request("GET", "/api/tasks")
        self.assertEqual(status, 200)
        self.assertIsInstance(body, list)
        self.assertGreaterEqual(len(body), 2)

    def test_create_patch_and_delete(self) -> None:
        status, task = request("POST", "/api/tasks", {"title": "Tarea de prueba"})
        self.assertEqual(status, 201)
        task_id = task["id"]
        self.assertEqual(task["title"], "Tarea de prueba")
        self.assertFalse(task["done"])

        status, patched = request("PATCH", f"/api/tasks/{task_id}", {"done": True})
        self.assertEqual(status, 200)
        self.assertTrue(patched["done"])
        self.assertEqual(patched["title"], "Tarea de prueba")

        status, _ = request("DELETE", f"/api/tasks/{task_id}")
        self.assertEqual(status, 204)

        status, body = request("PATCH", f"/api/tasks/{task_id}", {"done": True})
        self.assertEqual(status, 404)
        self.assertEqual(body["detail"], "Tarea no encontrada")

    def test_empty_title_is_rejected(self) -> None:
        status, _ = request("POST", "/api/tasks", {"title": ""})
        self.assertEqual(status, 422)


if __name__ == "__main__":
    unittest.main()
