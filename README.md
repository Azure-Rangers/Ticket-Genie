# Ticket-Genie
This project is an intelligent ticketing platform designed to streamline workplace support by automating routine employee inquiries and administrative workflows.

## How to Run

### Azure SQL Password

If you need the database admin password for local testing or deployment setup, retrieve it from Azure Key Vault:

```bash
az keyvault secret show --vault-name kv-app-prod-12345 --name db-admin-password --query value -o tsv
```

### Option 1: Run with Docker (Recommended)

The project uses a multi-stage Dockerfile to build either the FastAPI backend or the Streamlit frontend container.

#### Run FastAPI Backend Container (Port 8000)
```bash
# Build the FastAPI backend container image
docker build --target backend -t ticket-genie-backend .

# Run the backend container at http://localhost:8000
docker run -p 8000:8000 ticket-genie-backend
```

#### Run Streamlit Frontend Container (Port 8501)
```bash
# Build the Streamlit frontend container image
docker build --target frontend -t ticket-genie-frontend .

# Run the frontend container at http://localhost:8501
docker run -p 8501:8501 ticket-genie-frontend
```

---

### Option 2: Run Natively

For local development without Docker:

```bash
# Log in to Azure (if accessing Azure resources)
az login

# Install core, backend, and dev dependencies
pip install -e '.[backend,dev]'
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
# Run pytest test suite (includes app and backend tests)
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
├── terraform/                  # Infrastructure definitions for Azure
│   ├── main.tf
│   └── variables.tf
├── tests/
│   ├── test_app.py
│   ├── test_backend_api.py     # FastAPI endpoint tests
│   └── test_services.py
├── .dockerignore
├── .gitignore
├── Dockerfile                  # Multi-stage Docker build file (backend & frontend)
├── pyproject.toml              # Central config for dependencies, Ruff, pytest
└── README.md
```

The repository follows a monorepo structure with a Streamlit frontend under `app/` and a FastAPI REST API backend service under `backend/`.