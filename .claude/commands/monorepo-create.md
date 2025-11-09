# Create New Subproject

I'll help you create a new Python subproject with all the necessary structure and configuration.

## Quick Create

To create a subproject, run:
```bash
./scripts/create_python_subproject.sh
```

You'll be prompted for:
1. **Name**: Use lowercase with underscores (e.g., `api_service`, `data_processor`)
2. **Description**: Brief description (or press Enter to auto-generate)
3. **Tests**: Include test setup? (y/n, recommend: y)

## What Gets Created

```
your_subproject/
├── __init__.py           # Package initialization
├── hello_world.py        # Starter code
└── tests/               # (if tests = y)
    ├── __init__.py
    └── test_sample.py    # Sample test

.devcontainer/
└── your_subproject/
    ├── devcontainer.json # VS Code config
    └── Dockerfile        # Container setup
```

Plus updates to:
- `pyproject.toml` - New Poetry dependency group
- `Makefile` - Lint and test targets
- `.azuredevops/qa_pipeline.yaml` - CI/CD steps (if tests included)

## Common Subproject Types

### 🌐 API Service
```bash
echo -e "api_service\nREST API service\ny" | ./scripts/create_python_subproject.sh

# Then add dependencies:
./scripts/add_library.sh api_service fastapi
./scripts/add_library.sh api_service uvicorn
./scripts/add_library.sh api_service pydantic
```

### 📊 Data Pipeline
```bash
echo -e "data_pipeline\nData processing pipeline\ny" | ./scripts/create_python_subproject.sh

# Then add dependencies:
./scripts/add_library.sh data_pipeline pandas
./scripts/add_library.sh data_pipeline numpy
./scripts/add_library.sh data_pipeline sqlalchemy
```

### 🖥️ CLI Application
```bash
echo -e "cli_app\nCommand line application\ny" | ./scripts/create_python_subproject.sh

# Then add dependencies:
./scripts/add_library.sh cli_app click
./scripts/add_library.sh cli_app rich
./scripts/add_library.sh cli_app colorama
```

### 🌐 Web UI
```bash
echo -e "web_ui\nWeb user interface\ny" | ./scripts/create_python_subproject.sh

# Then add dependencies:
./scripts/add_library.sh web_ui streamlit
./scripts/add_library.sh web_ui plotly
./scripts/add_library.sh web_ui pandas
```

### 🔧 Shared Utilities
```bash
echo -e "common\nShared utilities and helpers\ny" | ./scripts/create_python_subproject.sh

# Then add common dependencies:
./scripts/add_library.sh common pydantic
./scripts/add_library.sh common pendulum
```

## After Creation

1. **Open in DevContainer**:
   - Press F1 → "Dev Containers: Reopen in Container"
   - Select your new subproject

2. **Install Dependencies**:
   ```bash
   poetry install --with your_subproject
   ```

3. **Start Coding**:
   - Edit `your_subproject/hello_world.py`
   - Run: `poetry run python your_subproject/hello_world.py`

4. **Run Tests**:
   ```bash
   make test-your_subproject
   make test-your_subproject-coverage
   ```

## Pro Tips

- **Naming**: Use descriptive names that indicate purpose
- **Tests**: Always include tests (default: yes)
- **Dependencies**: Add only what you need
- **Shared Code**: Put reusable utilities in a `common` subproject
- **DevContainers**: Use them for consistent environments