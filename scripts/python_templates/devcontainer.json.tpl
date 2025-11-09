{
  "name": "{{SUBPROJECT}} Development",
  "build": {
    "dockerfile": "Dockerfile",
    "context": "../.."
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-azuretools.vscode-docker",
        "ms-python.black-formatter",
        "charliermarsh.ruff",
        "esbenp.prettier-vscode"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/workspace/.venv/bin/python",
        "python.analysis.extraPaths": ["/workspace/{{SUBPROJECT}}"],
        "python.formatting.provider": "black",
        "python.formatting.blackArgs": [
          "--config",
          "/workspace/pyproject.toml"
        ],
        "python.linting.enabled": true,
        "python.linting.ruffEnabled": true,
        "python.linting.ruffArgs": ["--config", "/workspace/pyproject.toml"],
        "python.sortImports.args": ["--profile", "black"],
        "[python]": {
          "editor.defaultFormatter": "ms-python.black-formatter"
        },
        "[markdown]": {
          "editor.defaultFormatter": "esbenp.prettier-vscode"
        },
        "[yaml]": {
          "editor.defaultFormatter": "esbenp.prettier-vscode"
        },
        "[json]": {
          "editor.defaultFormatter": "esbenp.prettier-vscode"
        },
        "editor.formatOnSave": true
      }
    }
  },
  "workspaceFolder": "/workspace",
  "workspaceMount": "source=${localWorkspaceFolder},target=/workspace,type=bind,consistency=cached",
  "postCreateCommand": "cd /workspace && poetry lock && poetry install --with dev,{{SUBPROJECT}} && poetry run pre-commit install",
  "remoteUser": "vscode",
  "remoteEnv": {
    "PYTHONPATH": "/workspace"
  }
}
