# ServicePulse: Uptime and Latency Monitor

A full-stack uptime and latency monitoring application built with FastAPI, React, PostgreSQL, and Docker.

## Features

*   **Poller:** An APScheduler-based poller hits registered REST endpoints and records status codes and latency.
*   **Incident Management:** Intelligent incident grouping prevents alert fatigue by grouping consecutive failures on the same endpoint into a single open incident.
*   **Dashboard:** A React dashboard visualizing uptime percentages and latency trends using Recharts.
*   **Containerized:** Ships as a unified Docker image containing the compiled React static files served by the FastAPI backend.
*   **CI Pipeline:** GitHub Actions workflow ensures the Pytest suite passes on every push before building the Docker image.

## Tech Stack

*   **Backend:** Python 3.12, FastAPI, SQLAlchemy (Async), asyncpg, APScheduler, Alembic
*   **Frontend:** React 18, Vite, Recharts, Axios, react-icons
*   **Database:** PostgreSQL 16
*   **Infrastructure:** Docker, Docker Compose, GitHub Actions

## Running Locally (Docker)

1.  Copy `.env.example` to `.env`:
    ```bash
    cp .env.example .env
    ```
2.  Start the services using Docker Compose:
    ```bash
    docker-compose up --build
    ```
3.  Access the dashboard at `http://localhost:8000`.

## Development Setup

### Backend

1.  Navigate to the backend directory: `cd backend`
2.  Create a virtual environment: `python -m venv venv && source venv/bin/activate`
3.  Install dependencies: `pip install -r requirements.txt`
4.  Run a local PostgreSQL database.
5.  Run Alembic migrations: `alembic upgrade head`
6.  Start the FastAPI dev server: `uvicorn app.main:app --reload`

### Frontend

1.  Navigate to the frontend directory: `cd frontend`
2.  Install dependencies: `npm install`
3.  Start the Vite dev server: `npm run dev`
4.  The Vite server will proxy API requests to the backend at `http://localhost:8000`.
