"""Seed the database with a sample board so it isn't empty on first run.

Run with: python seed.py
"""
from db import get_connection, init_db, DB_PATH
import os


def seed():
    # Start fresh so re-running this script gives predictable data
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("INSERT INTO boards (name) VALUES (?)", ("Product Launch",))
    board_id = cur.lastrowid

    columns = ["To Do", "In Progress", "Done"]
    column_ids = {}
    for i, name in enumerate(columns):
        cur.execute(
            "INSERT INTO columns (board_id, name, position) VALUES (?, ?, ?)",
            (board_id, name, i),
        )
        column_ids[name] = cur.lastrowid

    tasks = [
        ("Write project spec", "Draft the initial requirements doc", "High", "To Do"),
        ("Set up repo", "Initialize git, CI, linting", "Medium", "To Do"),
        ("Design database schema", None, "High", "In Progress"),
        ("Build task API", "CRUD endpoints for tasks", "High", "In Progress"),
        ("Set up CI pipeline", None, "Low", "To Do"),
        ("Wireframe the board UI", None, "Medium", "Done"),
        ("Pick a tech stack", "React + Flask + SQLite", "Medium", "Done"),
    ]
    for title, description, priority, column_name in tasks:
        cur.execute(
            "INSERT INTO tasks (column_id, title, description, priority) VALUES (?, ?, ?, ?)",
            (column_ids[column_name], title, description, priority),
        )

    conn.commit()
    conn.close()
    print(f"Seeded database at {DB_PATH} with board_id={board_id}")


if __name__ == "__main__":
    seed()
