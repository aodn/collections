# --------------------------------------------------------------------
# --- Base Target ---
# --------------------------------------------------------------------
FROM prefecthq/prefect-aws:0.7.9-python3.12-prefect3.7.5 AS base

# --------------------------------------------------------------------
# --- App Target ---
# --------------------------------------------------------------------
FROM base AS app
WORKDIR /app

# Copy everything needed for the application install at once
COPY requirements.txt dist/*.whl ./

# Install app
RUN uv pip install --system --compile-bytecode -r requirements.txt *.whl

# --------------------------------------------------------------------
# --- Local Dev App Target ---
# --------------------------------------------------------------------
FROM app AS app-local-dev

# Local-only AWS credentials for Docker debugging.
# Populate .docker/local-aws/credentials and optionally .docker/local-aws/config.
COPY .docker/local-aws/ /root/.aws/

# --------------------------------------------------------------------
# --- Test Target ---
# --------------------------------------------------------------------
FROM app AS test

# Copy over the test folder and structural files needed to install dev dependencies
COPY tests/ ./tests/
COPY pyproject.toml README.md ./

# Install dev dependencies
ENV SETUPTOOLS_SCM_PRETEND_VERSION=0.0.0
RUN uv pip install --system --group dev

# Run tests
RUN pytest tests/ -v