import { useState } from "react";

export default function TaskForm({ initialTask, columnName, onSubmit, onCancel }) {
  const [title, setTitle] = useState(initialTask?.title || "");
  const [description, setDescription] = useState(initialTask?.description || "");
  const [priority, setPriority] = useState(initialTask?.priority || "Medium");
  const [titleError, setTitleError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const isEditing = Boolean(initialTask);

  async function handleSubmit(e) {
    e.preventDefault();
    const trimmed = title.trim();
    if (!trimmed) {
      setTitleError("Title can't be empty.");
      return;
    }
    setTitleError("");
    setSubmitting(true);
    try {
      await onSubmit({ title: trimmed, description: description.trim() || null, priority });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="modal-backdrop" onClick={onCancel}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>{isEditing ? "Edit task" : `New task${columnName ? ` in ${columnName}` : ""}`}</h2>
        <form onSubmit={handleSubmit}>
          <label className="field">
            Title
            <input
              autoFocus
              value={title}
              onChange={(e) => {
                setTitle(e.target.value);
                if (titleError) setTitleError("");
              }}
              placeholder="e.g. Write the onboarding email"
            />
            {titleError && <span className="field-error">{titleError}</span>}
          </label>

          <label className="field">
            Description <span className="optional">(optional)</span>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Any extra detail..."
            />
          </label>

          <label className="field">
            Priority
            <select value={priority} onChange={(e) => setPriority(e.target.value)}>
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
            </select>
          </label>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onCancel}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? "Saving..." : isEditing ? "Save changes" : "Create task"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
