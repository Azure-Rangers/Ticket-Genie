# Ticket-Genie
This project is an intelligent ticketing platform designed to streamline workplace support by automating routine employee inquiries and administrative workflows.

## How to Run

### Azure SQL Password

If you need the database admin password for local testing or deployment setup, retrieve it from Azure Key Vault:

```bash
az keyvault secret show --vault-name kv-app-prod-12345 --name db-admin-password --query value -o tsv
```

### Option 1: Run in Docker (Recommended)

Build and run the application in an isolated container:

```bash
# Build the container image
docker build -t ticket-genie .

# Run the container locally at http://localhost:8501
docker run -p 8501:8501 ticket-genie
```

### Option 2: Run Natively

For local development and testing without Docker:

```bash
# Install package dependencies with dev extras
pip install -e '.[dev]'

# Launch Streamlit app
streamlit run app/main.py
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
│       ├── pr-checks.yml       # Ruff linting, pytest, & terraform validation
│       └── deploy-prod.yml     # Infrastructure apply + Azure Pipelines handoff
├── app/
│   ├── main.py                 # Main Streamlit entrypoint (Home page)
│   ├── pages/                  # Multi-page Streamlit views
│   │   ├── 1_dashboard.py
│   │   └── 2_settings.py
│   ├── components/             # Custom UI component functions
│   └── services/               # Backend logic, DB calls, API integration
├── terraform/                  # Infrastructure definitions for Azure
│   ├── main.tf
│   └── variables.tf
├── tests/
│   ├── test_services.py
│   └── test_app.py
├── .dockerignore
├── .gitignore
├── Dockerfile                  # Container build instructions
├── pyproject.toml              # Central config for dependencies, Ruff, pytest
└── README.md
```

The app is organized under `app/` with a Streamlit entrypoint, multi-page views, reusable UI components, and backend services.