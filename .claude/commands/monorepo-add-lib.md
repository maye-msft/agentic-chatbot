# Add Library to Subproject

I'll help you add Python packages to specific subprojects using Poetry's dependency groups.

## Quick Add

```bash
./scripts/add_library.sh <subproject> <library> [version]
```

Examples:
```bash
./scripts/add_library.sh api_service fastapi
./scripts/add_library.sh analytics pandas 2.0.0
./scripts/add_library.sh cli_app click
```

## Common Libraries by Type

### 🌐 API Development
```bash
# FastAPI stack
./scripts/add_library.sh api_service fastapi
./scripts/add_library.sh api_service uvicorn
./scripts/add_library.sh api_service pydantic
./scripts/add_library.sh api_service python-multipart

# Flask stack
./scripts/add_library.sh api_service flask
./scripts/add_library.sh api_service flask-cors
./scripts/add_library.sh api_service flask-sqlalchemy

# Authentication
./scripts/add_library.sh api_service python-jose[cryptography]
./scripts/add_library.sh api_service passlib[bcrypt]
./scripts/add_library.sh api_service python-multipart
```

### 📊 Data Processing
```bash
# Core data tools
./scripts/add_library.sh data_pipeline pandas
./scripts/add_library.sh data_pipeline numpy
./scripts/add_library.sh data_pipeline polars

# Databases
./scripts/add_library.sh data_pipeline sqlalchemy
./scripts/add_library.sh data_pipeline psycopg2-binary
./scripts/add_library.sh data_pipeline pymongo

# File handling
./scripts/add_library.sh data_pipeline openpyxl
./scripts/add_library.sh data_pipeline python-docx
./scripts/add_library.sh data_pipeline PyPDF2
```

### 🖥️ CLI Applications
```bash
# CLI frameworks
./scripts/add_library.sh cli_app click
./scripts/add_library.sh cli_app typer
./scripts/add_library.sh cli_app fire

# Terminal UI
./scripts/add_library.sh cli_app rich
./scripts/add_library.sh cli_app colorama
./scripts/add_library.sh cli_app tqdm
./scripts/add_library.sh cli_app tabulate
```

### 🌐 Web UI
```bash
# Streamlit stack
./scripts/add_library.sh web_ui streamlit
./scripts/add_library.sh web_ui plotly
./scripts/add_library.sh web_ui altair

# Gradio for ML
./scripts/add_library.sh web_ui gradio
./scripts/add_library.sh web_ui pillow

# Dash for analytics
./scripts/add_library.sh web_ui dash
./scripts/add_library.sh web_ui dash-bootstrap-components
```

### 🧪 Testing & Quality
```bash
# Testing
./scripts/add_library.sh any_project pytest-asyncio
./scripts/add_library.sh any_project pytest-mock
./scripts/add_library.sh any_project pytest-cov
./scripts/add_library.sh any_project faker

# Type checking
./scripts/add_library.sh any_project types-requests
./scripts/add_library.sh any_project types-pyyaml
```

### 🔧 Utilities
```bash
# HTTP clients
./scripts/add_library.sh utils requests
./scripts/add_library.sh utils httpx
./scripts/add_library.sh utils aiohttp

# Date/Time
./scripts/add_library.sh utils pendulum
./scripts/add_library.sh utils python-dateutil

# Configuration
./scripts/add_library.sh utils python-dotenv
./scripts/add_library.sh utils pyyaml
./scripts/add_library.sh utils toml
```

## After Adding Libraries

1. **Install the dependencies**:
   ```bash
   poetry install --with <subproject>
   ```

2. **If DevContainer is running**, rebuild it:
   - Press F1 → "Dev Containers: Rebuild Container"

3. **Import in your code**:
   ```python
   import fastapi  # or whatever you added
   ```

## Check Installed Libraries

```bash
# Show all dependencies for a subproject
poetry show --only <subproject>

# Show dependency tree
poetry show --tree

# Check what's installed
grep "\[tool.poetry.group.<subproject>.dependencies\]" -A 10 pyproject.toml
```

## Troubleshooting

### If the script fails:

1. **Check subproject exists**:
   ```bash
   ls -d <subproject>/
   ```

2. **Verify Poetry group exists**:
   ```bash
   grep "\[tool.poetry.group.<subproject>\]" pyproject.toml
   ```

3. **Add manually if needed**:
   ```bash
   poetry add <library> --group <subproject>
   ```

4. **Clear Poetry cache**:
   ```bash
   poetry cache clear pypi --all
   ```

## Version Management

```bash
# Add specific version
./scripts/add_library.sh api_service "fastapi==0.104.0"

# Add with constraints
poetry add "pandas>=2.0,<3.0" --group analytics

# Update a library
poetry update pandas --group analytics

# Show outdated packages
poetry show --outdated
```