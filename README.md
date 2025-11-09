# Project Name

[Your project description here]

## 🚀 Quick Start

```bash
# Install dependencies
poetry install --with dev

# Run tests
make test-all

# Fix code issues
make lint-all
```

## 📂 Project Structure

```text
project-name/
├── subproject1/        # [Description of subproject1]
├── subproject2/        # [Description of subproject2]
├── common/            # Shared utilities
├── scripts/           # Automation scripts
└── .devcontainer/     # Development containers
```

## 🛠️ Development

### Create New Subproject

```bash
./scripts/create_python_subproject.sh
```

### Add Dependencies

```bash
./scripts/add_library.sh <subproject> <library>
```

### Use DevContainers

1. Open in VS Code
2. Press `F1` → "Dev Containers: Reopen in Container"
3. Select your subproject

## 🤖 Claude Code Commands

- `/monorepo-admin` - Intelligent assistant for all tasks
- `/monorepo-intro` - Quick reference guide
- `/monorepo-create` - Create new subprojects
- `/monorepo-add-lib` - Add dependencies

## 📚 Documentation

- [Getting Started](GETTING_STARTED.md) - First steps with your new monorepo
- [Template Guide](TEMPLATE_GUIDE.md) - Complete guide for using this monorepo template
- [Contributing](CONTRIBUTING.md) - How to contribute to this project
- [API Documentation](docs/api.md) - API reference (if applicable)

## 📋 Requirements

- Python 3.10+
- Poetry
- Docker (for DevContainers)
- VS Code with Remote-Containers extension

## 🧪 Testing

```bash
# Run all tests
make test-all

# Test specific subproject
make test-<subproject>

# Test with coverage
make test-<subproject>-coverage
```

## 📝 License

[Your license here]

## 🆘 Support

[Your support information here]

---

*This project was bootstrapped with [Monorepo Python Template](https://github.com/maye-msft/monorepo-python-template)*
