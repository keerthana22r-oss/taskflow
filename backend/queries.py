"""All raw SQL for the app lives here, kept separate from the Flask routes
so the query logic is easy to find, read, and unit-test on its own.
"""


def get_board(conn, board_id):
    return conn.execute("SELECT * FROM boards WHERE id = ?", (board_id,)).fetchone()


def get_columns_for_board(conn, board_id):
    return conn.execute(
        "SELECT * FROM columns WHERE board_id = ? ORDER BY position", (board_id,)
    ).fetchall()


def get_tasks_for_column(conn, column_id, priority=None):
    if priority:
        return conn.execute(
            "SELECT * FROM tasks WHERE column_id = ? AND priority = ? ORDER BY created_at DESC",
            (column_id, priority),
        ).fetchall()
    return conn.execute(
        "SELECT * FROM tasks WHERE column_id = ? ORDER BY created_at DESC", (column_id,)
    ).fetchall()


def create_task(conn, column_id, title, description, priority):
    cur = conn.execute(
        "INSERT INTO tasks (column_id, title, description, priority) VALUES (?, ?, ?, ?)",
        (column_id, title, description, priority),
    )
    conn.commit()
    return cur.lastrowid


def update_task(conn, task_id, title, description, priority):
    conn.execute(
        "UPDATE tasks SET title = ?, description = ?, priority = ? WHERE id = ?",
        (title, description, priority, task_id),
    )
    conn.commit()


def move_task(conn, task_id, new_column_id):
    conn.execute("UPDATE tasks SET column_id = ? WHERE id = ?", (new_column_id, task_id))
    conn.commit()


def delete_task(conn, task_id):
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()


def get_task(conn, task_id):
    return conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()


def column_belongs_to_board(conn, column_id, board_id):
    row = conn.execute(
        "SELECT 1 FROM columns WHERE id = ? AND board_id = ?", (column_id, board_id)
    ).fetchone()
    return row is not None


# --- The two required "non-trivial" queries ---------------------------------

def task_counts_per_column(conn, board_id):
    """Count of tasks per column on a given board, including columns with zero tasks.

    Uses a LEFT JOIN + GROUP BY so empty columns still show up with count 0,
    rather than filtering everything client-side after fetching all rows.
    """
    return conn.execute(
        """
        SELECT c.id AS column_id, c.name AS column_name, COUNT(t.id) AS task_count
        FROM columns c
        LEFT JOIN tasks t ON t.column_id = c.id
        WHERE c.board_id = ?
        GROUP BY c.id, c.name
        ORDER BY c.position
        """,
        (board_id,),
    ).fetchall()


def tasks_by_priority_newest_first(conn, board_id, priority):
    """All tasks of a given priority on a board, newest first, joined with column name."""
    return conn.execute(
        """
        SELECT t.id, t.title, t.description, t.priority, t.created_at,
               c.id AS column_id, c.name AS column_name
        FROM tasks t
        JOIN columns c ON c.id = t.column_id
        WHERE c.board_id = ? AND t.priority = ?
        ORDER BY t.created_at DESC
        """,
        (board_id, priority),
    ).fetchall()
