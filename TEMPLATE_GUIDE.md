# Monorepo Python Template - Complete Guide

This is the comprehensive documentation for the Monorepo Python Template. If you're using this template for your project, this guide will help you understand all features and capabilities.

> **Note:** The `README.md` in your project is a placeholder for your project-specific documentation. This guide contains all template-related information.

## 🚀 Features

- **Monorepo Architecture**: Manage multiple Python applications in a single repository
- **Isolated Dependencies**: Each subproject maintains its own dependencies via Poetry groups
- **DevContainers**: Consistent development environments using VS Code DevContainers
- **Code Quality Tools**: Pre-configured Black, Ruff, MyPy, and more
- **Automation Scripts**: Quick subproject creation and dependency management
- **Claude Code Integration**: Custom slash commands for common tasks

## 📚 Template Introduction

This template provides a structured approach to building Python monorepos, where multiple related applications and libraries can coexist in a single repository while maintaining clean separation of concerns.

### Why Use This Template?

- **Shared Code Reusability**: Easy sharing of common utilities across subprojects
- **Consistent Development**: All team members work in identical environments via DevContainers
- **Automated Workflows**: Scripts handle repetitive tasks like project creation and dependency management
- **Quality Assurance**: Pre-configured linting, formatting, and testing tools
- **Scalability**: Add new subprojects without affecting existing ones

### How It Works

1. Each subproject lives in its own directory with isolated dependencies
2. Poetry manages dependencies through separate groups for each subproject
3. DevContainers provide consistent development environments
4. Automation scripts handle project scaffolding and dependency management
5. GitHub Copilot prompts guide you through common tasks

## 🏗️ Repository Structure

```
monorepo-python-template/
├── .azuredevops/          # CI/CD pipeline configuration
│   └── qa_pipeline.yaml   # Quality assurance pipeline
├── .devcontainer/         # VS Code DevContainers (created per subproject)
├── .github/
│   └── prompts/          # GitHub Copilot custom prompts
│       ├── monorepo-admin.prompt.md
│       ├── monorepo-intro.prompt.md
│       ├── monorepo-create-subproject.prompt.md
│       └── monorepo-add-library.prompt.md
├── scripts/              # Automation scripts
│   ├── create_python_subproject.sh  # Create new subprojects
│   ├── add_library.sh               # Add dependencies
│   └── python_templates/            # Templates for new subprojects
├── pyproject.toml        # Poetry configuration and tool settings
├── Makefile             # Development commands
├── .pre-commit-config.yaml  # Pre-commit hooks configuration
└── README.md            # This file
```

## 🚦 Quick Start

### Prerequisites

- [VS Code](https://code.visualstudio.com/)
- [Docker](https://www.docker.com/) (for DevContainers)
- [Poetry](https://python-poetry.org/) (for dependency management)
- [Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- [GitHub Copilot](https://github.com/features/copilot) (optional, for prompt features)

### Getting Started

1. **Use as Template or Clone**
   ```bash
   # Option 1: Use GitHub's "Use this template" button
   # Option 2: Clone directly
   git clone https://github.com/maye-msft/monorepo-python-template.git my-monorepo
   cd my-monorepo
   ```

2. **Install Base Dependencies**
   ```bash
   poetry install --with dev
   ```

3. **Create Your First Subproject**
   ```bash
   ./scripts/create_python_subproject.sh
   # Interactive prompts will guide you through:
   # - Subproject name
   # - Description
   # - Whether to include tests
   ```

4. **Open in DevContainer**
   - Press `F1` in VS Code
   - Select "Dev Containers: Reopen in Container"
   - Choose your subproject's container

## 🔧 Automation Scripts

### 1. Create New Subproject

**Script:** `scripts/create_python_subproject.sh`

**What it creates:**
- Project directory with `__init__.py` and `hello_world.py`
- DevContainer configuration for isolated development
- Poetry dependency group in `pyproject.toml`
- Makefile targets for linting and testing
- Optional test directory with sample tests
- CI/CD pipeline steps (if tests are included)

**Usage:**
```bash
# Interactive mode
./scripts/create_python_subproject.sh

# You'll be prompted for:
# - Subproject name (e.g., api_service, data_processor)
# - Description (or auto-generated from name)
# - Add tests? (y/n, defaults to y)
```

**Example Output:**
```
✅ Python subproject 'api_service' created successfully!
- Location: ./api_service
- DevContainer: .devcontainer/api_service/
- Hello world: ./api_service/hello_world.py
- Tests: ./api_service/tests/test_sample.py
- Makefile targets added
- Poetry group added
```

### 2. Add Library to Subproject

**Script:** `scripts/add_library.sh`

**Purpose:** Add Python packages to specific subprojects using Poetry's dependency groups.

**Usage:**
```bash
# Add latest version
./scripts/add_library.sh <subproject> <library>

# Add specific version
./scripts/add_library.sh <subproject> <library> <version>
```

**Examples:**
```bash
# Add FastAPI to api_service subproject
./scripts/add_library.sh api_service fastapi

# Add specific version of pandas to analytics subproject
./scripts/add_library.sh analytics pandas 2.0.0

# Add multiple libraries
./scripts/add_library.sh api_service uvicorn
./scripts/add_library.sh api_service pydantic
```

## 🤖 GitHub Copilot Prompts

This template includes custom Copilot prompts to streamline your workflow. Use these in VS Code's Copilot chat:

### Available Prompts

#### `/monorepo-admin`
**Purpose:** Intelligent assistant that understands your intent and manages tasks

**Usage:**
```
# Natural language requests
"I need to build a REST API"
"Add pandas to my analytics project"
"Help, my poetry lock is failing"
"DevContainer won't start"
```

**Capabilities:**
- Understands natural language and chooses appropriate actions
- Creates subprojects based on your description
- Manages dependencies intelligently
- Troubleshoots Poetry and DevContainer issues
- Provides proactive suggestions for next steps

#### `/monorepo-intro`
**Purpose:** Display a quick reference guide for the template

**Usage:**
```
# In Copilot chat, type:
/monorepo-intro
```

**What it shows:**
- Repository structure overview
- Available scripts and their usage
- Essential Make commands
- Key concepts and quick start steps

#### `/monorepo-create-subproject`
**Purpose:** Interactive subproject creation with intelligent defaults

**Usage:**
```
# Basic usage
/monorepo-create-subproject

# Or provide details directly:
"Create a subproject called api_service"
"Create analytics for data processing with tests"
```

**Features:**
- Auto-generates description if not provided
- Defaults to including tests (best practice)
- Validates naming conventions
- Executes the creation script automatically

#### `/monorepo-add-library`
**Purpose:** Add dependencies to specific subprojects

**Usage:**
```
# Interactive mode
/monorepo-add-library

# Direct commands
"Add fastapi to api_service"
"Add pandas version 2.0.0 to analytics"
"Install requests in my_scraper"
```

**Smart Features:**
- Suggests common libraries based on subproject type:
  - CLI apps: `click`, `typer`, `rich`
  - APIs: `fastapi`, `flask`, `uvicorn`
  - Data: `pandas`, `numpy`, `polars`
  - Web UI: `streamlit`, `gradio`, `dash`

### How to Access Prompts

1. **Quick Access in Copilot Chat:**
   - Type `/` to see available prompts
   - Select or type the prompt name

2. **Command Palette:**
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Chat: Run Prompt"
   - Select the desired prompt

## 🛠️ Development Workflow

### Working with DevContainers

Each subproject gets its own DevContainer for isolated development:

1. **Open in Container:**
   - Press `F1` → "Dev Containers: Reopen in Container"
   - Select your subproject's container

2. **Automatic Setup:**
   - Poetry installs all dependencies
   - VS Code extensions are pre-configured
   - Python interpreter is set correctly

### Essential Commands

```bash
# Code Quality
make lint-all          # Fix all code issues automatically
make check-all         # Check without fixing
make test-all          # Run all tests

# Subproject-specific (added by creation script)
make lint-<subproject>         # Lint specific subproject
make test-<subproject>         # Test specific subproject
make test-<subproject>-coverage  # Test with coverage report

# Dependencies
poetry install --with <subproject>  # Install subproject dependencies
poetry add <package> --group <subproject>  # Add new dependency
```

### Dependency Management

Each subproject maintains isolated dependencies:

```bash
# Using Poetry directly
poetry add requests --group api_service
poetry add "pandas>=2.0" --group analytics

# Using the convenience script
./scripts/add_library.sh api_service requests
./scripts/add_library.sh analytics pandas 2.0.0
```

## ⚙️ Configuration

### Code Quality Tools

Pre-configured in `pyproject.toml`:

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **Black** | Code formatting | 120 char lines, Python 3.10+ |
| **Ruff** | Fast linting | E/F/B/D/I rules enabled |
| **MyPy** | Static type checking | Strict mode enabled |
| **Pydoclint** | Docstring validation | Google style |
| **PyMarkdown** | Markdown linting | Relaxed rules |
| **Yamllint** | YAML validation | Standard rules |

### Pre-commit Hooks

Automatic code quality checks on commit:

```bash
# Install hooks
poetry run pre-commit install

# Run manually
poetry run pre-commit run --all-files

# Skip hooks (not recommended)
git commit --no-verify
```

## 📋 CI/CD Pipeline

The Azure DevOps pipeline (`.azuredevops/qa_pipeline.yaml`) runs on pull requests:

1. **Setup:** Python 3.10, Poetry installation
2. **Dependencies:** Install all project dependencies
3. **Linting:** Run all code quality checks
4. **Testing:** Execute tests for each subproject (added by creation script)

## 💡 Best Practices

1. **Project Organization:**
   - Create a `common` or `shared` subproject for reusable utilities
   - Keep subprojects focused on single responsibilities
   - Use meaningful names that describe the subproject's purpose

2. **Dependency Management:**
   - Keep dependencies isolated per subproject
   - Pin critical dependency versions for production
   - Regularly update dependencies with `poetry update`

3. **Code Quality:**
   - Always run `make lint-all` before committing
   - Write tests for new functionality (included by default)
   - Use type hints for better IDE support and error catching

4. **Development Workflow:**
   - Use DevContainers for consistent environments
   - Leverage Copilot prompts for common tasks
   - Create subprojects using the script for consistency

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Create your subproject: `./scripts/create_python_subproject.sh`
4. Add necessary dependencies: `./scripts/add_library.sh`
5. Write tests in the `tests/` subdirectory
6. Run quality checks: `make lint-all && make test-all`
7. Submit a pull request

## 📝 License

This template is provided as-is for use in your projects. Customize as needed for your specific requirements.

## 🆘 Support

- **Quick Help:** Type `/monorepo-intro` in Copilot chat
- **Scripts:** Check `scripts/` directory for automation tools
- **Configuration:** Review `pyproject.toml` for tool settings
- **Issues:** Report at [GitHub Issues](https://github.com/maye-msft/monorepo-python-template/issues)