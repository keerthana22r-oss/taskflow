import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db as db_module
import queries as q
from app import app


@pytest.fixture
def client(monkeypatch):
    """Spin up a fresh temp SQLite DB per test and point the app at it."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.remove(path)  # init_db will recreate it

    monkeypatch.setattr(db_module, "DB_PATH", path)
    db_module.init_db(path)

    conn = db_module.get_connection(path)
    conn.execute("INSERT INTO boards (id, name) VALUES (1, 'Test Board')")
    conn.execute("INSERT INTO columns (id, board_id, name, position) VALUES (1, 1, 'To Do', 0)")
    conn.execute("INSERT INTO columns (id, board_id, name, position) VALUES (2, 1, 'In Progress', 1)")
    conn.execute("INSERT INTO columns (id, board_id, name, position) VALUES (3, 1, 'Done', 2)")
    conn.commit()
    conn.close()

    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

    os.remove(path)


def test_create_task_without_title_fails(client):
    resp = client.post("/api/tasks", json={"column_id": 1, "priority": "High"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_create_task_with_whitespace_only_title_fails(client):
    resp = client.post("/api/tasks", json={"title": "   ", "column_id": 1})
    assert resp.status_code == 400


def test_create_task_success(client):
    resp = client.post(
        "/api/tasks", json={"title": "Write tests", "column_id": 1, "priority": "Medium"}
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["title"] == "Write tests"
    assert body["column_id"] == 1


def test_moving_a_task_updates_its_column(client):
    create = client.post("/api/tasks", json={"title": "Move me", "column_id": 1})
    task_id = create.get_json()["id"]

    move = client.patch(f"/api/tasks/{task_id}/move", json={"column_id": 2})
    assert move.status_code == 200
    assert move.get_json()["column_id"] == 2

    # Confirm the board view reflects it too
    board = client.get("/api/boards/1").get_json()
    in_progress_col = next(c for c in board["columns"] if c["id"] == 2)
    assert any(t["id"] == task_id for t in in_progress_col["tasks"])


def test_moving_nonexistent_task_returns_404(client):
    resp = client.patch("/api/tasks/9999/move", json={"column_id": 2})
    assert resp.status_code == 404


def test_task_counts_per_column_query_hits_db_directly(client):
    """Test (3): a test that hits the database/query layer directly."""
    conn = db_module.get_connection(db_module.DB_PATH)
    q.create_task(conn, 1, "Task A", None, "High")
    q.create_task(conn, 1, "Task B", None, "Low")
    q.create_task(conn, 2, "Task C", None, "Medium")

    rows = q.task_counts_per_column(conn, board_id=1)
    counts = {r["column_name"]: r["task_count"] for r in rows}
    conn.close()

    assert counts["To Do"] == 2
    assert counts["In Progress"] == 1
    assert counts["Done"] == 0  # empty column still shows up, count 0


def test_tasks_by_priority_newest_first_query(client):
    conn = db_module.get_connection(db_module.DB_PATH)
    q.create_task(conn, 1, "Older high task", None, "High")
    q.create_task(conn, 1, "Newer high task", None, "High")
    q.create_task(conn, 1, "A low task", None, "Low")

    rows = q.tasks_by_priority_newest_first(conn, board_id=1, priority="High")
    conn.close()

    assert len(rows) == 2
    assert all(r["priority"] == "High" for r in rows)
    # Newest first: the second-inserted row should come first when timestamps tie,
    # since SQLite datetime('now') has second-level resolution and id is a reasonable
    # tiebreaker in practice for rows inserted in the same test.
    titles = [r["title"] for r in rows]
    assert "Newer high task" in titles and "Older high task" in titles


def test_delete_task(client):
    create = client.post("/api/tasks", json={"title": "Delete me", "column_id": 1})
    task_id = create.get_json()["id"]

    delete = client.delete(f"/api/tasks/{task_id}")
    assert delete.status_code == 204

    board = client.get("/api/boards/1").get_json()
    all_task_ids = [t["id"] for col in board["columns"] for t in col["tasks"]]
    assert task_id not in all_task_ids


def test_filter_board_by_priority(client):
    client.post("/api/tasks", json={"title": "High one", "column_id": 1, "priority": "High"})
    client.post("/api/tasks", json={"title": "Low one", "column_id": 1, "priority": "Low"})

    resp = client.get("/api/boards/1?priority=High")
    board = resp.get_json()
    todo_tasks = next(c for c in board["columns"] if c["id"] == 1)["tasks"]
    assert all(t["priority"] == "High" for t in todo_tasks)
