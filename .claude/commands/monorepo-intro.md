# Monorepo Python Template - Quick Reference

## 📂 Repository Structure

```text
monorepo-python-template/
├── scripts/             # Automation scripts
│   ├── create_python_subproject.sh  # Create new subprojects
│   └── add_library.sh               # Add dependencies
├── .devcontainer/       # DevContainers (created per subproject)
├── .claude/commands/    # Claude Code custom commands
├── pyproject.toml       # Poetry dependencies
└── Makefile            # Development commands
```

## 🚀 Essential Commands

### Create New Subproject

```bash
./scripts/create_python_subproject.sh
# Interactive prompts for name, description, tests
```

### Add Library

```bash
./scripts/add_library.sh <subproject> <library> [version]
# Example: ./scripts/add_library.sh api_service fastapi
```

### Code Quality

```bash
make lint-all      # Fix all code issues
make check-all     # Check without fixing
make test-all      # Run all tests
```

## 🤖 Available Claude Commands

- `/monorepo-admin` - Natural language assistant
- `/monorepo-intro` - This quick reference
- `/monorepo-create` - Create new subproject
- `/monorepo-add-lib` - Add dependencies

## 🐳 DevContainers

1. Press `F1` in VS Code
2. Select "Dev Containers: Reopen in Container"
3. Choose your subproject's container
4. Poetry installs dependencies automatically

## 💡 Key Concepts

- **Isolated Dependencies**: Each subproject has its own Poetry group
- **Shared Code**: Create a `common` subproject for utilities
- **DevContainers**: Consistent development environments
- **Quality Tools**: Pre-configured Black, Ruff, MyPy, etc.

## 📋 Quick Workflow

1. **Create subproject**: `/monorepo-create api_service`
2. **Add dependencies**: `/monorepo-add-lib api_service fastapi`
3. **Open in DevContainer**: F1 → Reopen in Container
4. **Start coding**: Edit files in your subproject
5. **Test & lint**: `make test-all && make lint-all`

## 📚 Documentation

- [Getting Started](../../GETTING_STARTED.md) - First steps
- [Template Guide](../../TEMPLATE_GUIDE.md) - Complete documentation
- [README](../../README.md) - Project overview
