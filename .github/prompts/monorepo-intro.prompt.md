---
mode: 'ask'
description: 'Learn how to use the Monorepo Python Template'
---

## Monorepo Python Template - Quick Guide

This template helps you manage multiple Python applications in a single repository with shared utilities and consistent development environments.

## Repository Structure

```text
monorepo-python-template/
├── scripts/             # Automation scripts
│   ├── create_python_subproject.sh  # Create new subprojects
│   └── add_library.sh               # Add dependencies
├── .devcontainer/       # VS Code DevContainer configs (created per subproject)
├── .github/prompts/     # Copilot prompts for automation
├── pyproject.toml       # Poetry dependencies
└── Makefile            # Development commands
```

## Available Scripts

### 1. Create New Subproject

```bash
./scripts/create_python_subproject.sh
# Enter: name, description, add tests (y/n)
```

### 2. Add Library to Subproject

```bash
./scripts/add_library.sh <subproject> <library> [version]
# Example: ./scripts/add_library.sh my_api requests
```

## Available Copilot Prompts

Use these in Copilot chat:

- `/monorepo-intro` - Show this guide
- `/monorepo-create-subproject` - Create new subproject interactively
- `/monorepo-add-library` - Add dependencies to subprojects

### Quick Examples

```text
# In Copilot chat:
/monorepo-create-subproject
"Create a subproject called api_service"

/monorepo-add-library
"Add fastapi to api_service"
"Add pandas version 2.0.0 to analytics"
```

## Essential Make Commands

```bash
make lint-all      # Fix all code issues
make check-all     # Check without fixing
make test-all      # Run all tests
make help          # Show all commands
```

## Working with DevContainers

1. Open VS Code
2. Press `F1` → "Dev Containers: Reopen in Container"
3. Choose appropriate container (cli/ui/utils)
4. Dependencies auto-install via Poetry

## Key Concepts

- **Isolated Dependencies**: Each subproject has its own Poetry group
- **Shared Utilities**: Create a common subproject for shared code
- **DevContainers**: Consistent development environments
- **Automated Quality**: Pre-commit hooks for code standards

## Quick Start

1. Create a subproject: `/monorepo-create-subproject` in Copilot
2. Add dependencies: `/monorepo-add-library` in Copilot
3. Open in DevContainer
4. Start coding!

For detailed documentation, see [TEMPLATE_GUIDE.md](../../TEMPLATE_GUIDE.md)
