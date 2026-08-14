import TaskCard from "./TaskCard";

export default function Column({ column, allColumns, onAddTask, onEdit, onDelete, onMove }) {
  return (
    <div className="column">
      <div className="column-header">
        <h3>{column.name}</h3>
        <span className="task-count">{column.tasks.length}</span>
      </div>

      <div className="task-list">
        {column.tasks.length === 0 && (
          <p className="empty-column">No tasks here.</p>
        )}
        {column.tasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            columns={allColumns}
            onEdit={onEdit}
            onDelete={onDelete}
            onMove={onMove}
          />
        ))}
      </div>

      <button className="add-task-btn" onClick={() => onAddTask(column)}>
        + Add task
      </button>
    </div>
  );
}
