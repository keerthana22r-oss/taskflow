# TaskFlow

A small task board app (React + Flask + SQLite) — boards contain columns, columns contain tasks.
Built as a take-home assignment.

## Stack

- **Frontend:** React (Vite, JavaScript)
- **Backend:** Python / Flask, raw SQL over `sqlite3` (no ORM — see "Database" below for why)
- **Database:** SQLite

## Project structure

```
taskflow/
├── backend/
│   ├── app.py           # Flask routes
│   ├── db.py             # connection + schema init
│   ├── queries.py        # all SQL lives here, separate from routes
│   ├── schema.sql         # CREATE TABLE statements
│   ├── seed.py            # seed script
│   ├── requirements.txt
│   └── tests/
│       └── test_app.py
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── components/    # Column, TaskCard, TaskForm
    │   └── api/client.js  # fetch wrapper + error handling
    └── ...
```

## Running it locally (fresh clone)

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py                  # creates taskflow.db with sample data
python app.py                   # runs on http://localhost:5000
```

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
cp .env.example .env            # points the frontend at http://localhost:5000/api
npm run dev                     # runs on http://localhost:5173
```

Open `http://localhost:5173`. You should see a "Product Launch" board with three columns and
sample tasks.

### Running tests

```bash
cd backend
python -m pytest tests/ -v
```

9 tests, covering: rejecting an empty/whitespace title, moving a task between columns, deleting
a task, the priority filter, and two tests that hit the query layer directly (`task_counts_per_column`
and `tasks_by_priority_newest_first`) against known seed-shaped data.

## Deployment

Deployed on Render as two services (backend as a Web Service, frontend as a Static Site).
`render.yaml` at the repo root defines both, so Render's "New Blueprint" flow can pick this up
directly.

- **Backend:** `gunicorn app:app`, with `ALLOWED_ORIGIN` set to the frontend's deployed URL
  (CORS defaults to allowing any origin locally, but is locked down in production).
- **Frontend:** static build (`npm run build`), with `VITE_API_URL` pointed at the backend's
  deployed URL + `/api`.
- If the database file doesn't exist when a request comes in (first boot, or after a redeploy
  on Render's free tier — see limitation below), the backend seeds it automatically rather than
  serving an empty board.

**Live links:**
- App: _add after deploying_
- API: _add after deploying_

**Known limitation:** Render's free tier uses an ephemeral filesystem, so the SQLite file can
reset on redeploy or after the instance spins down from inactivity. That's fine for a reviewer
clicking around (auto-seed re-populates it), but it means data isn't durable across restarts —
a real deployment would use a persistent disk or a managed Postgres instance instead.

## Database

The schema (`backend/schema.sql`) has three tables — `boards`, `columns`, `tasks` — each with an
`INTEGER PRIMARY KEY`, a foreign key down the chain (`tasks.column_id → columns.id`,
`columns.board_id → boards.id`, both `ON DELETE CASCADE`), and `NOT NULL` on required fields
(`title`, `name`). `priority` has a `CHECK` constraint restricting it to `Low` / `Medium` / `High`.

A task's "status" is just which column it's in — there's no separate `status` column, since
`column_id` already encodes that and a second field would just be a value that could drift out
of sync with it.

I used raw SQL (`sqlite3` module) instead of an ORM. For a schema this small an ORM wasn't
necessary, and it made it easy to write the two required non-trivial queries as actual SQL rather
than fetching everything and filtering in Python (`backend/queries.py`):

- **`task_counts_per_column`** — `LEFT JOIN` + `GROUP BY` so columns with zero tasks still show
  up with a count of 0, instead of only counting columns that have at least one task.
- **`tasks_by_priority_newest_first`** — joins `tasks` to `columns` (to scope by board) and
  filters + sorts in SQL rather than pulling all tasks into Python and filtering there.

Both are exposed as read-only stats endpoints (`/api/boards/:id/stats/...`) as well as being unit
tested directly against the DB layer.

## Assumptions & decisions

- **Single board, hardcoded ID.** The assignment scopes out multiple boards/teams, so the
  frontend always loads `board_id = 1` (seeded by `seed.py`) rather than building board
  selection UI that wasn't asked for.
- **Move via dropdown, not drag-and-drop.** Chose the dropdown-on-each-card approach per the
  assignment's own guidance ("a working dropdown beats a broken drag-and-drop") to keep the
  time budget on the core requirements and the two required SQL queries.
- **Priority filter is server-side**, not client-side — the filter is passed as a query param and
  applied in the SQL `WHERE` clause, consistent with the emphasis on querying the DB rather than
  filtering everything after fetching it all.
- **Optimistic UI on move**, with a revert-and-reload if the request fails, so drag-free
  column moves still feel responsive.
- **No search box** — called out as a nice-to-have, skipped in favor of making sure the core
  flow (create/edit/move/delete, all persisted, all validated) was solid.

## What I'd improve with more time

- Deploy it (Render for the backend + a static host for the frontend) so there's a live link.
- Add a text search box (the other nice-to-have) and a small "N tasks" badge per column header
  using the `task_counts_per_column` query, both listed as stretch goals.
- Debounce/optimistic-update the edit form the same way moves are optimistic.
- Add a couple of frontend component tests (React Testing Library) — the assignment asked
  specifically for backend tests, so I prioritized those, but I'd want frontend coverage too
  for a real project.

## Time spent

Roughly 3–4 hours end to end: schema + backend + tests first, then the React frontend, then
this write-up.

## Something I found interesting

Writing `task_counts_per_column` with a `LEFT JOIN` instead of an `INNER JOIN` was a good reminder
of a mistake that's easy to make under time pressure — an inner join silently drops any column
that currently has zero tasks, which for a "To Do / In Progress / Done" board is exactly the kind
of state (an empty "Done" column on day one) you actually want to see reflected in the count.
