# Ticket-Genie
This project is an intelligent ticketing platform designed to streamline workplace support by automating routine employee inquiries and administrative workflows.

## How to Run

Create or activate the project virtual environment, install the dependencies, and start the Streamlit app:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -e '.[dev]'
streamlit run app/main.py
```

If you are using the checked-in project environment, you can also run:

```bash
.venv311/bin/python -m pytest
streamlit run app/main.py
```

If editable install still fails, remove the old virtual environment and recreate it with the commands above so it picks up the current Python and pip versions.

## Streamlit Layout

The app is organized under `app/` with a Streamlit entrypoint, multi-page views, reusable UI components, and backend services.


# Branching Strategy
Use short-lived branches for active work:

- `feature/<short-desc>` or `feat/<issue-id>` for new capabilities.
- `fix/<issue-id>` or `bugfix/<short-desc>` for non-urgent bug fixes.
- `hotfix/<issue-id>` for urgent production fixes.

Keep `main` reserved for production-ready changes. Pull requests should include testing steps, linked issues, and any relevant safety notes using the PR template in `.github/PULL_REQUEST_TEMPLATE.md`.

# Directory

Ticket-Genie/
├── .github/
│   └── workflows/
│       ├── pr-checks.yml       # Ruff linting, pytest, & terraform validation
│       └── deploy-prod.yml     # Infrastructure apply + Azure Pipelines handoff
├── app/
│   ├── main.py                 # Main Streamlit entrypoint (Home page)
│   ├── pages/                  # Multi-page Streamlit views (automatically detected)
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
├── .gitignore
├── pyproject.toml              # Central config for dependencies, Ruff, pytest
└── README.md