import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "taskflow.db")


def get_connection(db_path=None):
    """Return a sqlite3 connection with foreign keys enforced and row access by column name."""
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=None):
    """Create tables from schema.sql if they don't already exist."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r") as f:
        schema = f.read()
    conn = get_connection(db_path)
    conn.executescript(schema)
    conn.commit()
    conn.close()
