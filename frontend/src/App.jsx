import { useEffect, useState, useCallback } from "react";
import Column from "./components/Column";
import TaskForm from "./components/TaskForm";
import { api, ApiError } from "./api/client";
import "./App.css";

const BOARD_ID = 1; // Single-board app — out of scope to support multiple boards/teams (see README)

export default function App() {
  const [board, setBoard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");

  const [formState, setFormState] = useState(null); // { mode: 'create'|'edit', task, column }
  const [pendingDelete, setPendingDelete] = useState(null);

  const loadBoard = useCallback(async (priority) => {
    setLoading(true);
    setError("");
    try {
      const data = await api.getBoard(BOARD_ID, priority || undefined);
      setBoard(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load the board.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadBoard(priorityFilter);
  }, [priorityFilter, loadBoard]);

  async function handleCreate(column) {
    setFormState({ mode: "create", column });
  }

  async function handleEdit(task) {
    setFormState({ mode: "edit", task });
  }

  async function handleFormSubmit(values) {
    setError("");
    try {
      if (formState.mode === "create") {
        await api.createTask({ ...values, column_id: formState.column.id });
      } else {
        await api.updateTask(formState.task.id, values);
      }
      setFormState(null);
      await loadBoard(priorityFilter);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't save the task.");
      throw err; // keep the form open so the user can retry
    }
  }

  async function handleMove(task, newColumnId) {
    // Optimistic update so the dropdown feels instant
    setBoard((prev) => {
      if (!prev) return prev;
      const columns = prev.columns.map((col) => ({
        ...col,
        tasks: col.tasks.filter((t) => t.id !== task.id),
      }));
      const target = columns.find((c) => c.id === newColumnId);
      target.tasks.unshift({ ...task, column_id: newColumnId });
      return { ...prev, columns };
    });

    try {
      await api.moveTask(task.id, newColumnId);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't move the task.");
      await loadBoard(priorityFilter); // revert to server truth
    }
  }

  async function confirmDelete() {
    if (!pendingDelete) return;
    try {
      await api.deleteTask(pendingDelete.id);
      setPendingDelete(null);
      await loadBoard(priorityFilter);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't delete the task.");
      setPendingDelete(null);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>TaskFlow</h1>
          <p className="subtitle">{board?.name || "Loading board..."}</p>
        </div>

        <label className="filter">
          Priority
          <select value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}>
            <option value="">All</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </label>
      </header>

      {error && (
        <div className="banner error-banner" role="alert">
          {error}
          <button onClick={() => setError("")} aria-label="Dismiss">
            ×
          </button>
        </div>
      )}

      {loading && !board && <p className="loading">Loading board...</p>}

      {board && (
        <div className="board">
          {board.columns.map((column) => (
            <Column
              key={column.id}
              column={column}
              allColumns={board.columns}
              onAddTask={handleCreate}
              onEdit={handleEdit}
              onDelete={setPendingDelete}
              onMove={handleMove}
            />
          ))}
        </div>
      )}

      {formState && (
        <TaskForm
          initialTask={formState.task}
          columnName={formState.column?.name}
          onSubmit={handleFormSubmit}
          onCancel={() => setFormState(null)}
        />
      )}

      {pendingDelete && (
        <div className="modal-backdrop" onClick={() => setPendingDelete(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Delete task?</h2>
            <p>
              "{pendingDelete.title}" will be permanently deleted. This can't be undone.
            </p>
            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setPendingDelete(null)}>
                Cancel
              </button>
              <button className="btn-danger" onClick={confirmDelete}>
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
