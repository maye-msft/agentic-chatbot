# Monorepo Admin Assistant

I'm your intelligent monorepo assistant. I understand natural language and can help with various tasks.

## What I Can Help With:

### 🚀 Creating Subprojects
Tell me what you want to build:
- "I need a REST API" → Creates `api_service` subproject
- "Create a data processor" → Creates `data_processor` subproject
- "Set up authentication" → Creates `auth_module` subproject

### 📦 Managing Dependencies
Tell me what to add and where:
- "Add fastapi to my API" → Installs fastapi in api subproject
- "Install pandas in analytics" → Adds pandas to analytics subproject
- "My scraper needs requests" → Adds requests to scraper subproject

### 🔧 Troubleshooting

#### Poetry Issues:
```bash
# Lock file problems
poetry lock --no-update
poetry install

# Dependency conflicts
poetry show --tree
poetry update

# Clear cache
poetry cache clear pypi --all
poetry install

# Reset environment
poetry env remove python
poetry install
```

#### DevContainer Issues:
1. **Rebuild**: F1 → "Dev Containers: Rebuild Container"
2. **Clean Rebuild**: F1 → "Dev Containers: Clean Rebuild Container"
3. **Check Logs**: F1 → "Dev Containers: Show Container Log"
4. **Reset Docker**: `docker system prune -a` (warning: removes all)

### 📋 Status Checks
```bash
# List subprojects
ls -d */ | grep -v scripts

# Show Poetry groups
grep "\[tool.poetry.group\." pyproject.toml

# Check structure
find . -maxdepth 2 -name "*.py" -o -name "tests"
```

## Quick Actions:

### Create API Service:
```bash
./scripts/create_python_subproject.sh
# Name: api_service
# Description: REST API service
# Tests: y

# Then add dependencies:
./scripts/add_library.sh api_service fastapi
./scripts/add_library.sh api_service uvicorn
./scripts/add_library.sh api_service pydantic
```

### Create Data Pipeline:
```bash
./scripts/create_python_subproject.sh
# Name: data_pipeline
# Description: Data processing pipeline
# Tests: y

# Then add dependencies:
./scripts/add_library.sh data_pipeline pandas
./scripts/add_library.sh data_pipeline numpy
./scripts/add_library.sh data_pipeline sqlalchemy
```

### Fix Code Issues:
```bash
make lint-all  # Fix all issues
make test-all  # Run all tests
make check-all # Check without fixing
```

## Tell me what you need!

Just describe what you want to do in natural language, and I'll help you accomplish it.