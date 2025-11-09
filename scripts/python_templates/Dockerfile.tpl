# Dockerfile for Python subproject
FROM mcr.microsoft.com/devcontainers/python:3.10

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry==1.6.1

# Configure poetry
RUN poetry config virtualenvs.in-project true

WORKDIR /workspace/{{SUBPROJECT}}
