# Use an official lightweight Python base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr for clean container logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory inside container
WORKDIR /app

# Ensure the project root is always importable when Streamlit runs app/main.py
ENV PYTHONPATH=/app

# Install system dependencies required for building C-extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definition file first to leverage Docker layer caching
COPY pyproject.toml .

# Copy application source before installation so the package is included in the image
COPY app/ ./app/

# Install dependencies (installing the project without dev extras)
RUN pip install --no-cache-dir .

# Expose Streamlit's default port
EXPOSE 8501

# Configure Streamlit healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Launch Streamlit app
ENTRYPOINT ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]