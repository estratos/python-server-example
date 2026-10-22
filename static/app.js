const list = document.querySelector("#tasks");
const form = document.querySelector("#new-task");
const input = document.querySelector("#title");
const empty = document.querySelector("#empty");
const error = document.querySelector("#error");

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `Error ${response.status}`);
  }
  return response.status === 204 ? null : response.json();
}

/** Crea el <li> de una tarea sin usar innerHTML (evita inyección de HTML). */
function renderTask(task) {
  const item = document.createElement("li");
  item.className = "task" + (task.done ? " is-done" : "");

  const label = document.createElement("label");
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = task.done;

  const title = document.createElement("span");
  title.className = "task-title";
  title.textContent = task.title;

  checkbox.addEventListener("change", async () => {
    checkbox.disabled = true;
    try {
      await api(`/api/tasks/${task.id}`, {
        method: "PATCH",
        body: JSON.stringify({ done: checkbox.checked }),
      });
      item.classList.toggle("is-done", checkbox.checked);
    } catch (err) {
      checkbox.checked = !checkbox.checked;
      showError(err);
    } finally {
      checkbox.disabled = false;
    }
  });

  const remove = document.createElement("button");
  remove.type = "button";
  remove.className = "task-remove";
  remove.textContent = "Eliminar";
  remove.addEventListener("click", async () => {
    remove.disabled = true;
    try {
      await api(`/api/tasks/${task.id}`, { method: "DELETE" });
      item.remove();
      empty.hidden = list.children.length > 0;
    } catch (err) {
      remove.disabled = false;
      showError(err);
    }
  });

  label.append(checkbox, title);
  item.append(label, remove);
  return item;
}

function showError(err) {
  error.textContent = err.message;
  error.hidden = false;
}

async function refresh() {
  try {
    const tasks = await api("/api/tasks");
    list.replaceChildren(...tasks.map(renderTask));
    empty.hidden = tasks.length > 0;
    error.hidden = true;
  } catch (err) {
    showError(err);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = input.value.trim();
  if (!title) return;

  const button = form.querySelector("button");
  button.disabled = true;
  try {
    const task = await api("/api/tasks", {
      method: "POST",
      body: JSON.stringify({ title }),
    });
    list.append(renderTask(task));
    empty.hidden = true;
    error.hidden = true;
    form.reset();
    input.focus();
  } catch (err) {
    showError(err);
  } finally {
    button.disabled = false;
  }
});

refresh();
