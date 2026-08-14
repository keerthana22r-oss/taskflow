const PRIORITY_STYLES = {
  High: { bg: "#fdecea", color: "#b3261e", label: "High" },
  Medium: { bg: "#fff4e0", color: "#9a6300", label: "Medium" },
  Low: { bg: "#e8f3ea", color: "#2e7d4f", label: "Low" },
};

export default function TaskCard({ task, columns, onEdit, onDelete, onMove }) {
  const priorityStyle = PRIORITY_STYLES[task.priority] || PRIORITY_STYLES.Medium;

  return (
    <div className="task-card">
      <div className="task-card-top">
        <span
          className="priority-pill"
          style={{ background: priorityStyle.bg, color: priorityStyle.color }}
        >
          {priorityStyle.label}
        </span>
        <div className="task-card-actions">
          <button className="icon-btn" onClick={() => onEdit(task)} aria-label="Edit task">
            Edit
          </button>
          <button
            className="icon-btn danger"
            onClick={() => onDelete(task)}
            aria-label="Delete task"
          >
            Delete
          </button>
        </div>
      </div>

      <p className="task-title">{task.title}</p>
      {task.description && <p className="task-description">{task.description}</p>}

      <div className="task-card-bottom">
        <label className="move-label">
          Move to
          <select
            value={task.column_id}
            onChange={(e) => onMove(task, Number(e.target.value))}
          >
            {columns.map((col) => (
              <option key={col.id} value={col.id}>
                {col.name}
              </option>
            ))}
          </select>
        </label>
      </div>
    </div>
  );
}
