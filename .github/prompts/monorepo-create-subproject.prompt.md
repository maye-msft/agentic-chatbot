---
mode: 'agent'
description: 'Create a new Python subproject using the automated script'
---

## Create a New Python Subproject

I'll help you create a new Python subproject in this monorepo using the automated creation script.

## Instructions for Copilot

When the user wants to create a new subproject:

1. **Collect the following information from the user:**
   - **Subproject name**: A descriptive name (e.g., `analytics`, `api_service`, `data_processor`)
   - **Description** (optional): A brief description of the subproject's purpose
   - **Include tests** (optional): Whether to add test files (defaults to 'y')

2. **Validate and process inputs:**
   - Use lowercase with underscores for the name (convert spaces/hyphens to underscores)
   - Avoid generic names like `test`, `main`, `app`
   - If no description provided, generate one from the name:
     - `analytics` → "Analytics and data processing module"
     - `api_service` → "API service module"
     - `auth_handler` → "Authentication handler module"
     - Default pattern: "{formatted_name} module"
   - If tests not specified, default to 'y' (include tests)
   - Convert the tests choice to lowercase 'y' or 'n'

3. **Execute the creation script:**

   Run the following command with the collected inputs:

   ```bash
   echo -e "{subproject_name}\n{description}\n{add_tests}" | ./scripts/create_python_subproject.sh
   ```

4. **What the script creates:**
   - `{subproject_name}/` directory with:
     - `__init__.py` (empty initialization file)
     - `hello_world.py` (simple main function with project name and description)
   - `.devcontainer/{subproject_name}/` with:
     - `devcontainer.json` (VS Code DevContainer configuration)
     - `Dockerfile` (container setup)
   - Updates to `pyproject.toml`:
     - New optional dependency group `[tool.poetry.group.{subproject_name}]`
   - If tests are included (y):
     - `{subproject_name}/tests/` directory with `test_sample.py`
     - Makefile targets: `test-{subproject_name}` and `test-{subproject_name}-coverage`
     - Azure DevOps pipeline step for running tests

5. **After successful creation, provide instructions:**
   - How to open in the new DevContainer
   - How to run the hello world example: `poetry run python {subproject_name}/hello_world.py`
   - How to run tests (if added): `make test-{subproject_name}`
   - How to add dependencies: `poetry add package_name --group {subproject_name}`

## Example Interactions

### Full interaction

User: "I want to create a new subproject for data analytics"

Copilot should:

1. Ask for the subproject name (suggest: `analytics` or `data_analytics`)
2. Ask for a description (optional - will generate if not provided)
3. Ask if tests should be included (optional - defaults to yes)
4. Run: `echo -e "analytics\nData analytics and visualization tools\ny" | ./scripts/create_python_subproject.sh`
5. Show the created files and next steps

### Minimal interaction

User: "Create a subproject called auth_service"

Copilot should:

1. Use the provided name: `auth_service`
2. Generate description: "Auth service module"
3. Default to including tests: `y`
4. Run: `echo -e "auth_service\nAuth service module\ny" | ./scripts/create_python_subproject.sh`
5. Show the created files and next steps

## Quick Commands

If the user provides partial or full information, process accordingly:

- "Create subproject api_service" → Generate description, default to tests
- "Create api_service for REST API" → Use "REST API" as description, default to tests
- "Create api_service for REST API service with tests" → Use all provided info
- Execute: `echo -e "api_service\nREST API service\ny" | ./scripts/create_python_subproject.sh`
