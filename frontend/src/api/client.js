const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

class ApiError extends Error {}

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch (err) {
    throw new ApiError("Couldn't reach the server. Check your connection and try again.");
  }

  if (!res.ok) {
    let message = "Something went wrong. Please try again.";
    try {
      const body = await res.json();
      if (body?.error) message = body.error;
    } catch {
      // response wasn't JSON, fall back to the default message
    }
    throw new ApiError(message);
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  getBoard: (boardId, priority) =>
    request(`/boards/${boardId}${priority ? `?priority=${priority}` : ""}`),

  createTask: (task) =>
    request("/tasks", { method: "POST", body: JSON.stringify(task) }),

  updateTask: (taskId, task) =>
    request(`/tasks/${taskId}`, { method: "PUT", body: JSON.stringify(task) }),

  moveTask: (taskId, columnId) =>
    request(`/tasks/${taskId}/move`, {
      method: "PATCH",
      body: JSON.stringify({ column_id: columnId }),
    }),

  deleteTask: (taskId) => request(`/tasks/${taskId}`, { method: "DELETE" }),
};

export { ApiError };
