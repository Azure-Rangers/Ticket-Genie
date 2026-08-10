# Ticket-Genie
This project is an intelligent ticketing platform designed to streamline workplace support by automating routine employee inquiries and administrative workflows.

## Production Architecture (Dual Azure Web Apps)

Ticket-Genie enforces a strict security boundary by separating the frontend UI and backend REST API into two distinct Azure Linux Web Apps:

```text
                                 ┌──────────────────────────────────────────────┐
                                 │   webapp-prod-frontend-ticketgenie           │
  User Browser ────────────────► │   - Streamlit UI (Port 8501)                 │
                                 │   - Holds NO database or API secrets         │
                                 └──────────────────────┬───────────────────────┘
                                                        │ REST API Calls
                                                        ▼
                                 ┌──────────────────────────────────────────────┐
                                 │   webapp-prod-backend-ticketgenie            │
                                 │   - FastAPI REST API (Port 8000)             │
                                 │   - Holds DB Connection & AI Secrets         │
                                 └──────────────────────┬───────────────────────┘
                                                        │ SQL Port 1433
                                                        ▼
                                           ┌─────────────────────────┐
                                           │  Azure SQL Database     │
                                           └─────────────────────────┘
```

- **Frontend App**: `webapp-prod-frontend-ticketgenie` (Streamlit on port 8501). Contains zero database or AI secrets and connects to the backend API via `BACKEND_API_URL`.
- **Backend App**: `webapp-prod-backend-ticketgenie` (FastAPI on port 8000). Serves API endpoints and securely accesses Azure SQL Database and Key Vault.

---

## Environment & Secrets Setup

Ticket-Genie uses a `.env` file for managing application configuration and secrets locally.

### Fetching Remote Secrets from Azure Key Vault

To securely fetch environment secrets locally from Azure Key Vault into a `.env` file (works cross-platform on **Windows**, **macOS**, and **Linux**):

```bash
# 1. Log in to Azure
az login

# 2. Run the secret fetch script to populate/update your local .env file
python fetch_secrets.py
```

#### Custom Vault Options:
```bash
# Fetch from specific Key Vault names
python fetch_secrets.py --vault-names kv-app-prod-12345 group-1

# Fetch from specific Key Vault URLs
python fetch_secrets.py --vault-urls https://kv-app-prod-12345.vault.azure.net/

# Output to custom env file location
python fetch_secrets.py --env-file .env.local
```

Both the **Streamlit Frontend** (`app/main.py`) and **FastAPI Backend** (`backend/main.py`) automatically load configuration from the `.env` file at startup using `python-dotenv`.

---

## How to Run

### Option 1: Run with Docker (Recommended)

The project uses a multi-stage Dockerfile to build either the FastAPI backend or the Streamlit frontend container.

#### Run FastAPI Backend Container (Port 8000)
```bash
# Build the FastAPI backend container image
docker build --target backend -t ticket-genie-backend .

# Run the backend container with local .env configuration at http://localhost:8000
docker run --env-file .env -p 8000:8000 ticket-genie-backend
```

#### Run Streamlit Frontend Container (Port 8501)
```bash
# Build the Streamlit frontend container image
docker build --target frontend -t ticket-genie-frontend .

# Run the frontend container with local .env configuration at http://localhost:8501
docker run --env-file .env -p 8501:8501 ticket-genie-frontend
```

---

### Option 2: Run Natively

For local development without Docker:

```bash
# Install core, backend, and dev dependencies
pip install -e '.[backend,dev]'

# Fetch secrets from Azure Key Vault into .env
az login
python fetch_secrets.py
```

#### Launch FastAPI Backend API
```bash
# Start Uvicorn dev server at http://localhost:8000
uvicorn backend.main:app --reload --port 8000
```
- API Health Check: `http://localhost:8000/health`
- Interactive Swagger Docs: `http://localhost:8000/docs`

#### Launch Streamlit Frontend App
```bash
# Launch Streamlit app at http://localhost:8501
streamlit run app/main.py
```

---

### Running Tests and Quality Checks

```bash
# Run pytest test suite (includes app, backend, and secret fetcher tests)
pytest

# Run Ruff linter and formatting check
ruff check .
ruff format --check .
```

## Branching Strategy

Use short-lived branches for active work:

- `feature/<short-desc>` or `feat/<issue-id>` for new capabilities.
- `fix/<issue-id>` or `bugfix/<short-desc>` for non-urgent bug fixes.
- `hotfix/<issue-id>` for urgent production fixes.

Keep `main` reserved for production-ready changes. Pull requests should include testing steps, linked issues, and any relevant safety notes using the PR template in `.github/PULL_REQUEST_TEMPLATE.md`.

## Directory Structure

```text
Ticket-Genie/
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       ├── pr-checks.yml       # Ruff linting, pytest, & Docker smoke testing
│       └── deploy-prod.yml     # ACR build/push & Azure handoff
├── app/                        # Streamlit Frontend
│   ├── main.py                 # Main Streamlit entrypoint (Home page)
│   ├── pages/                  # Multi-page Streamlit views
│   │   ├── 1_dashboard.py
│   │   └── 2_settings.py
│   ├── components/             # Custom UI component functions
│   └── services/               # UI backend logic & API integration
├── backend/                    # FastAPI Backend Service
│   ├── main.py                 # FastAPI application entrypoint
│   ├── api/                    # API route controllers
│   ├── models/                 # Pydantic data schemas
│   ├── services/               # Business logic services
│   ├── database/               # Database connection & CRUD handlers
│   └── requirements.txt        # Backend dependencies (-e .[backend])
├── scripts/
│   └── fetch_secrets.py        # Entrypoint for fetching Key Vault secrets
├── terraform/                  # Infrastructure definitions for Azure
│   ├── main.tf
│   ├── outputs.tf
│   └── variables.tf
├── tests/
│   ├── test_app.py
│   ├── test_backend_api.py     # FastAPI endpoint tests
│   ├── test_fetch_secrets.py   # Secret fetcher tests
│   └── test_services.py
├── .dockerignore
├── .gitignore
├── Dockerfile                  # Multi-stage Docker build file (backend & frontend)
├── fetch_secrets.py            # Cross-platform Azure Key Vault to .env fetcher script
├── pyproject.toml              # Central config for dependencies, Ruff, pytest
└── README.md
```

The repository follows a monorepo structure with a Streamlit frontend under `app/` and a FastAPI REST API backend service under `backend/`.