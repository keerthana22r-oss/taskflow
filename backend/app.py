from flask import Flask, request, jsonify
from flask_cors import CORS

from db import get_connection, init_db, DB_PATH
import queries as q
import os

app = Flask(__name__)

# In dev, allow any origin (simplest for localhost). In production, set
# ALLOWED_ORIGIN to your deployed frontend's URL so the API isn't wide open.
allowed_origin = os.environ.get("ALLOWED_ORIGIN")
CORS(app, origins=[allowed_origin] if allowed_origin else "*")


def row_to_task(row):
    return {
        "id": row["id"],
        "column_id": row["column_id"],
        "title": row["title"],
        "description": row["description"],
        "priority": row["priority"],
        "created_at": row["created_at"],
    }


@app.before_request
def ensure_db_exists():
    # Safety net: if the DB file is missing (first boot, or Render's free-tier
    # disk reset on redeploy), seed it with sample data rather than serving
    # an empty, unusable board.
    if not os.path.exists(DB_PATH):
        from seed import seed
        seed()


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Something went wrong on the server"}), 500


# --- Board -------------------------------------------------------------------

@app.route("/api/boards/<int:board_id>", methods=["GET"])
def get_board_with_columns_and_tasks(board_id):
    conn = get_connection()
    board = q.get_board(conn, board_id)
    if board is None:
        conn.close()
        return jsonify({"error": "Board not found"}), 404

    priority_filter = request.args.get("priority")

    columns = q.get_columns_for_board(conn, board_id)
    result_columns = []
    for col in columns:
        tasks = q.get_tasks_for_column(conn, col["id"], priority=priority_filter)
        result_columns.append({
            "id": col["id"],
            "name": col["name"],
            "position": col["position"],
            "tasks": [row_to_task(t) for t in tasks],
        })

    conn.close()
    return jsonify({
        "id": board["id"],
        "name": board["name"],
        "columns": result_columns,
    })


# --- Tasks ---------------------------------------------------------------

@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    description = data.get("description")
    priority = data.get("priority") or "Medium"
    column_id = data.get("column_id")

    if not title:
        return jsonify({"error": "Title is required"}), 400
    if priority not in ("Low", "Medium", "High"):
        return jsonify({"error": "Priority must be Low, Medium, or High"}), 400
    if not column_id:
        return jsonify({"error": "column_id is required"}), 400

    conn = get_connection()
    try:
        task_id = q.create_task(conn, column_id, title, description, priority)
    except Exception:
        conn.close()
        return jsonify({"error": "Could not create task. Check that column_id is valid."}), 400

    task = q.get_task(conn, task_id)
    conn.close()
    return jsonify(row_to_task(task)), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def edit_task(task_id):
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    description = data.get("description")
    priority = data.get("priority") or "Medium"

    if not title:
        return jsonify({"error": "Title is required"}), 400
    if priority not in ("Low", "Medium", "High"):
        return jsonify({"error": "Priority must be Low, Medium, or High"}), 400

    conn = get_connection()
    existing = q.get_task(conn, task_id)
    if existing is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    q.update_task(conn, task_id, title, description, priority)
    task = q.get_task(conn, task_id)
    conn.close()
    return jsonify(row_to_task(task))


@app.route("/api/tasks/<int:task_id>/move", methods=["PATCH"])
def move_task(task_id):
    data = request.get_json(silent=True) or {}
    new_column_id = data.get("column_id")
    if not new_column_id:
        return jsonify({"error": "column_id is required"}), 400

    conn = get_connection()
    existing = q.get_task(conn, task_id)
    if existing is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    q.move_task(conn, task_id, new_column_id)
    task = q.get_task(conn, task_id)
    conn.close()
    return jsonify(row_to_task(task))


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_connection()
    existing = q.get_task(conn, task_id)
    if existing is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    q.delete_task(conn, task_id)
    conn.close()
    return "", 204


# --- Stats (the two required non-trivial queries, exposed for the UI too) ---

@app.route("/api/boards/<int:board_id>/stats/counts-per-column", methods=["GET"])
def counts_per_column(board_id):
    conn = get_connection()
    rows = q.task_counts_per_column(conn, board_id)
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/boards/<int:board_id>/stats/by-priority", methods=["GET"])
def by_priority(board_id):
    priority = request.args.get("priority", "High")
    conn = get_connection()
    rows = q.tasks_by_priority_newest_first(conn, board_id, priority)
    conn.close()
    return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        init_db()
    app.run(debug=True, port=5000)
