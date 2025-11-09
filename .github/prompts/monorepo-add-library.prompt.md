---
mode: 'agent'
description: 'Add a library to a specific subproject using Poetry'
---

# Add Library to Subproject

I'll help you add a library/package to a specific subproject in this monorepo using Poetry.

## Instructions for Copilot

When the user wants to add a library to a subproject:

1. **Collect the following information from the user:**
   - **Subproject name**: Which subproject to add the library to (e.g., `api_service`, `data_processor`, or any custom subproject)
   - **Library name**: The package to install (e.g., `requests`, `pandas`, `fastapi`)
   - **Version** (optional): Specific version if needed (e.g., `2.31.0`)

2. **Validate inputs:**
   - Check if the subproject exists by verifying the directory
   - Ensure the library name is valid (no special characters except hyphens and underscores)
   - Version format should be semantic versioning if provided

3. **Execute the add library script:**
   Run the following command with the collected inputs:
   ```bash
   ./scripts/add_library.sh {subproject_name} {library_name} [version]
   ```

4. **What the script does:**
   - Validates the subproject exists
   - Checks that Poetry group exists for the subproject
   - Uses Poetry to add the library to the specific group
   - Updates `pyproject.toml` and `poetry.lock`
   - Shows success message with next steps

5. **After successful addition, inform the user:**
   - Library has been added to the subproject's dependencies
   - How to use it: `import {library_name}` in the subproject code
   - The DevContainer will automatically have the library available
   - How to manually install: `poetry install --with {subproject_name}`

## Example Interactions

### Basic library addition:
User: "Add requests to my_api"

Copilot should:
1. Extract: subproject=`my_api`, library=`requests`
2. Run: `./scripts/add_library.sh my_api requests`
3. Confirm successful addition

### With specific version:
User: "Add pandas version 2.0.0 to the analytics subproject"

Copilot should:
1. Extract: subproject=`analytics`, library=`pandas`, version=`2.0.0`
2. Run: `./scripts/add_library.sh analytics pandas 2.0.0`
3. Confirm successful addition

### Interactive mode:
User: "I need to add a library"

Copilot should:
1. Ask which subproject (list available ones if helpful)
2. Ask which library to add
3. Ask if a specific version is needed (optional)
4. Run: `./scripts/add_library.sh {subproject} {library} {version}`
5. Confirm successful addition

## Common Libraries by Subproject Type

Suggest these based on subproject type:
- **CLI applications**: `click`, `typer`, `rich`, `colorama`
- **Web UI**: `streamlit`, `gradio`, `dash`, `plotly`
- **API services**: `fastapi`, `flask`, `uvicorn`, `pydantic`
- **Data processing**: `pandas`, `numpy`, `polars`, `duckdb`
- **Utils/Common**: `pendulum`, `requests`, `httpx`, `pyyaml`

## Error Handling

If the script fails, check for:
- Subproject doesn't exist → Suggest creating it first with `/monorepo-create-subproject`
- Poetry group missing → The script will show how to fix it
- Library not found → Verify the package name on PyPI
- Version conflict → Try without version or check compatibility