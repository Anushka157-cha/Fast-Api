# 🚀 Task Manager API (FastAPI)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Anushka157-cha/Fast-Api)

A production-ready, secure, and modular RESTful API built with **FastAPI**, **SQLAlchemy ORM**, **Alembic**, **Pydantic v2**, and **PyJWT**.

---

## ✨ Features

- **CRUD & Filtering:** Complete operations for tasks with status filtering, keyword search, and pagination (`skip` & `limit`).
- **JWT Authentication:** Password hashing using Argon2 (`pwdlib`), token creation, distinct expired/invalid token handling, and `/auth/me` profile endpoint.
- **User Isolation:** Secure data segregation—users can only read, update, or delete their own tasks (prevents IDOR vulnerabilities).
- **Centralized Configuration:** Type-safe environment management via **Pydantic Settings** (`config.py`).
- **CORS & Middleware:** Configured CORS middleware supporting web & mobile clients, plus automatic request latency tracking (`X-Process-Time` header).
- **Health Checks & Observability:** Production-ready `/health` endpoint checking DB connectivity and structured request logging.
- **Input Validation & Clean Errors:** Strict Pydantic models with `EmailStr`, title whitespace trimming, and duplicate checking (409).
- **Database Architecture & Migrations:** Modular SQLAlchemy models with 1-to-many relationships, cascade deletion, and automated schema migrations via **Alembic**.
- **Automated Testing:** 23 automated integration and unit tests using **Pytest** and an isolated in-memory SQLite database.
- **Containerization & CI/CD:** Non-root secure **Docker** image, `.env.example`, and automated GitHub Actions CI pipeline.

---

## 📁 Project Architecture

```text
├── alembic/              # Database migration scripts
├── routers/
│   ├── auth.py           # Authentication routes (/auth/signup, /auth/login, /auth/me)
│   └── tasks.py          # Task routes (/tasks CRUD, search, pagination)
├── tests/
│   ├── conftest.py       # Pytest fixtures and isolated in-memory test DB
│   ├── test_auth.py      # Authentication test suite
│   ├── test_health.py    # Health check, CORS, latency tests
│   └── test_tasks.py     # Task operations and user isolation test suite
├── config.py             # Centralized Pydantic Settings
├── database.py           # Engine and session configuration (with connection pooling)
├── models.py             # SQLAlchemy ORM models (UserDB, TaskDB)
├── schemas.py            # Pydantic v2 request/response schemas
├── security.py           # JWT token generation, verification, and password hashing
├── main.py               # FastAPI application entry point with CORS & middleware
├── Dockerfile            # Production Docker image configuration (non-root user)
├── requirements.txt      # Production dependencies
└── .github/workflows/    # GitHub Actions automated test workflow
```

---

## 🛠️ Local Setup & Installation

### 1. Clone the repository & create a virtual environment
```bash
git clone https://github.com/your-username/fastapi-task-manager.git
cd fastapi-task-manager

# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup environment variables
Copy `.env.example` to `.env` and configure your secret key:
```bash
cp .env.example .env
```
In `.env`:
```env
JWT_SECRET_KEY=your_secure_random_secret_key_here
DATABASE_URL=sqlite:///./tasks.db
```

### 4. Run database migrations
```bash
alembic upgrade head
```

### 5. Start the server
```bash
uvicorn main:app --reload
```
Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser for the interactive Swagger UI!

---

## 🧪 Running Automated Tests

Run the full automated test suite with Pytest:
```bash
pytest -v
```

---

## 🐳 Running with Docker

Build and run using Docker:
```bash
docker build -t task-manager-api .
docker run -p 8000:8000 --env-file .env task-manager-api
```

---

## 🌐 Free Cloud Deployment (e.g. Render.com)

1. Push this repository to **GitHub**.
2. Go to [Render.com](https://render.com) and create a new **Web Service**.
3. Connect your GitHub repository.
4. Set the following settings:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt && alembic upgrade head`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. In **Environment Variables**, add:
   - `JWT_SECRET_KEY` = `your_strong_random_secret_key`
6. Click **Deploy Web Service** — Your API is now live on the internet! 🚀
