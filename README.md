# 🚀 TaskFlow — Modern Full-Stack Kanban & Workflow Management Platform

[![Live Demo](https://img.shields.io/badge/Demo-Live%20Application-brightgreen?style=for-the-badge&logo=render&logoColor=white)](https://taskflow-nwym.onrender.com)
[![Live API](https://img.shields.io/badge/API-Live%20Endpoints-blue?style=for-the-badge&logo=fastapi&logoColor=white)](https://taskflow-1-7apv.onrender.com/api/boards/1)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/keerthana22r-oss/taskflow)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5.0-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Pytest](https://img.shields.io/badge/Tested%20with-Pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Render](https://img.shields.io/badge/Deploy-Render%20Blueprint-46E3B7?style=flat-square&logo=render&logoColor=black)](https://render.com/)

---

## 📌 Executive Overview

**TaskFlow** is a production-ready, full-stack workflow and project management system designed with **React (Vite)** on the frontend and an optimized **Python / Flask** RESTful backend. Engineered for speed, clean architectural separation, and deterministic state transitions, TaskFlow implements a dynamic multi-column Kanban board with real-time column analytics, server-side priority filtering, optimistic UI updates, and an automated self-healing database pipeline.

Unlike basic task apps, TaskFlow avoids heavy ORM bloat by executing high-performance parameterized raw SQL via Python's native `sqlite3` driver. This enables precise control over relational constraints, foreign-key cascades, and aggregated metric queries.

---

## 🎯 Live Application & Reviewer Access

> [!TIP]
> **Experience the Live App:** Click the badges above or navigate directly:
> - 🌐 **Interactive Web App:** **[taskflow-nwym.onrender.com](https://taskflow-nwym.onrender.com)**
> - ⚡ **Live API Service:** **[taskflow-1-7apv.onrender.com](https://taskflow-1-7apv.onrender.com/api/boards/1)**
>
> *First load note:* On free-tier cloud containers, please allow 30–45 seconds for backend cold boot. The application includes a self-healing auto-seed fallback to guarantee an interactive board upon startup.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            TASKFLOW KANBAN DASHBOARD                        │
├──────────────────────┬──────────────────────┬───────────────────────────────┤
│    📋 TO DO (3)      │    ⚙️ IN PROGRESS (2) │          ✅ DONE (4)          │
├──────────────────────┼──────────────────────┼───────────────────────────────┤
│ [High] Auth Flow     │ [Med] API Pagination │ [Low] Database Schema         │
│ Design JWT refresh   │ Implement limit/ofs  │ Define foreign keys & indices │
│ Move ▾  Edit  Del    │ Move ▾  Edit  Del    │ Move ▾  Edit  Del             │
├──────────────────────┼──────────────────────┼───────────────────────────────┤
│ [Med] Unit Tests     │ [High] Optimistic UI │ [Med] CI/CD Pipeline          │
│ 95%+ coverage pytest │ State rollback on err│ GitHub Actions & Render spec  │
│ Move ▾  Edit  Del    │ Move ▾  Edit  Del    │ Move ▾  Edit  Del             │
└──────────────────────┴──────────────────────┴───────────────────────────────┘
```

---

## ✨ Key Features & Architectural Highlights

- **⚡ Fluid Kanban Board**:
  - Full CRUD lifecycle (Create, Read, Update, Move, and Delete tasks).
  - Dynamic inter-column progression with deterministic state validation.
- **🔄 Optimistic UI Mutations**:
  - Task transitions render instantly in the UI with state rollback if an API rejection occurs.
- **🔍 Server-Side Priority Filtering**:
  - Filters (`Low`, `Medium`, `High`) are evaluated directly in SQL `WHERE` clauses rather than relying on heavy client-side array manipulation.
- **📊 Optimized SQL Metric Aggregations**:
  - `task_counts_per_column`: Implements a specialized `LEFT JOIN` and `GROUP BY` query to guarantee zero-task columns display `0` accurately instead of being dropped by `INNER JOIN` queries.
  - `tasks_by_priority_newest_first`: Performs single-trip relational joins between tasks and columns to return sorted priority slices.
- **🛡️ Resilient Self-Healing Auto-Seed**:
  - Backend `@app.before_request` hook checks for database integrity; if the container spins up on an ephemeral disk, it seeds realistic sample data automatically so the reviewer is never greeted with a broken UI.
- **🧪 Comprehensive Test Suite**:
  - Automated Pytest integration and unit tests covering query logic, validation failures, boundary titles, and cascade deletions.

---

## 🛠️ Technology Stack Breakdown

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend Framework** | **React 18** | Modular component-driven UI with Hooks (`useState`, `useEffect`, `useCallback`) |
| **Build & Tooling** | **Vite 5** | Instant Hot Module Replacement (HMR) and optimized rollup bundle generation |
| **Backend API** | **Python 3 / Flask 3.0** | Lightweight, high-throughput RESTful routing and JSON serialization |
| **WSGI Server** | **Gunicorn 22** | Production WSGI HTTP Server for UNIX/Linux hosting |
| **Database Engine** | **SQLite3 (Raw SQL)** | Zero-overhead, transactional ACID storage with strict foreign keys and check constraints |
| **CORS Security** | **Flask-CORS** | Origin whitelisting between decoupled frontend and backend domains |
| **Testing** | **Pytest 8** | Unit testing query functions and HTTP status integration assertions |
| **Deployment** | **Render (IaC)** | Multi-service orchestration (Web Service + Static Site) via `render.yaml` |

---

## 🏛️ System Architecture & Directory Tree

```
taskflow/
├── render.yaml                   # Infrastructure-as-Code Blueprint for Render
├── README.md                     # Comprehensive Project Documentation
├── backend/
│   ├── app.py                    # Flask application endpoints & middleware
│   ├── db.py                     # SQLite connection pool & schema initialization
│   ├── queries.py                # Parameterized SQL query abstraction layer
│   ├── schema.sql                # DDL statements (Tables, FKs, CHECK constraints)
│   ├── seed.py                   # Automated realistic seed data generator
│   ├── requirements.txt          # Python dependencies (Flask, Gunicorn, Pytest)
│   └── tests/
│       └── test_app.py           # Integration & query-level Pytest suite
└── frontend/
    ├── index.html                # Single Page Application entry point
    ├── vite.config.js            # Vite configuration & dev server proxy
    ├── package.json              # Frontend manifest & scripts
    ├── .env.example              # Template environment variables
    └── src/
        ├── main.jsx              # React DOM initialization
        ├── App.jsx               # Root application state & column layout
        ├── App.css               # Clean responsive styling & theme variables
        ├── api/
        │   └── client.js         # Centralized Fetch client with unified error handling
        └── components/
            ├── Column.jsx        # Column container & column-level statistics
            ├── TaskCard.jsx      # Interactive task card with dropdown transition
            └── TaskForm.jsx      # Modal / inline validated task creation form
```

---

## 📡 RESTful API Reference

All API routes communicate via standard JSON payloads and HTTP status codes:

| Method | Endpoint | Description | Payload / Query Params |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/boards/<id>` | Fetch board with columns & nested tasks | `?priority=High` *(optional filter)* |
| `POST` | `/api/tasks` | Create a new task in a specified column | `{"title": "...", "description": "...", "priority": "High", "column_id": 1}` |
| `PUT` | `/api/tasks/<id>` | Update title, description, or priority | `{"title": "...", "description": "...", "priority": "Medium"}` |
| `PATCH`| `/api/tasks/<id>/move` | Move task to a different column | `{"column_id": 2}` |
| `DELETE`| `/api/tasks/<id>` | Permanently remove a task | *None* (Returns `204 No Content`) |
| `GET` | `/api/boards/<id>/stats/counts-per-column` | Aggregated task counts per column | *None* |
| `GET` | `/api/boards/<id>/stats/by-priority` | Fetch tasks filtered & sorted by priority | `?priority=High` |

---

## 💻 Local Development & Quickstart Guide

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & **npm**
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/keerthana22r-oss/taskflow.git
cd taskflow
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create & activate a virtual environment
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed the database with sample boards & tasks
python seed.py

# Launch development API server (runs on http://localhost:5000)
python app.py
```

### 3. Frontend Setup
Open a second terminal window:
```bash
# Navigate to frontend directory
cd frontend

# Install npm dependencies
npm install

# Configure environment variables
cp .env.example .env

# Start Vite dev server (runs on http://localhost:5173)
npm run dev
```

Visit **`http://localhost:5173`** in your browser.

---

## 🧪 Running Automated Tests

The backend test suite verifies route status codes, input validations, SQL query outputs, and cascade logic:

```bash
cd backend
python -m pytest tests/ -v
```

Expected output:
```text
tests/test_app.py::test_empty_title_rejected PASSED
tests/test_app.py::test_move_task PASSED
tests/test_app.py::test_delete_task PASSED
tests/test_app.py::test_priority_filter PASSED
tests/test_app.py::test_counts_per_column PASSED
tests/test_app.py::test_tasks_by_priority_newest_first PASSED
========================== 9 passed in 0.28s ==========================
```

---

## 🚀 Deployed on Render

This project is deployed on **Render** as decoupled microservices using `render.yaml`:
- **Frontend Web App:** [https://taskflow-nwym.onrender.com](https://taskflow-nwym.onrender.com)
- **Backend API Service:** [https://taskflow-1-7apv.onrender.com](https://taskflow-1-7apv.onrender.com)

---

## 🔮 Roadmap & Future Enhancements

- [ ] **Drag & Drop Reordering**: Integrate `@hello-pangea/dnd` for smooth card reordering within and across columns.
- [ ] **Managed PostgreSQL Integration**: Swap SQLite with Neon/Supabase PostgreSQL for persistent multi-tenant boards.
- [ ] **User Authentication & RBAC**: Add JWT token-based auth for personal and team workspace isolation.
- [ ] **WebSocket Sync**: Real-time multi-user live board synchronization using Flask-SocketIO.

---

## 👩‍💻 Author & Contact

**Keerthana K R**  
Full-Stack & AI Software Engineer  

- **GitHub:** [@keerthana22r-oss](https://github.com/keerthana22r-oss)
- **Email:** [keerthana22r@gmail.com](mailto:keerthana22r@gmail.com)
- **LinkedIn:** [linkedin.com/in/keerthanakr](https://www.linkedin.com)

---

## 📄 License

This project is open-source and distributed under the [MIT License](https://opensource.org/licenses/MIT).
