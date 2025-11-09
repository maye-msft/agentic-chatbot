# Getting Started with Your Monorepo

Welcome! You've just created a project from the Monorepo Python Template. Here's how to get started:

## ✅ First Steps

### 1. Update Project Information

Edit `README.md` and replace:
- `# Project Name` with your actual project name
- `[Your project description here]` with your project description
- `[Your license here]` with your license choice
- `[Your support information here]` with contact/support details

### 2. Update Poetry Configuration

Edit `pyproject.toml`:
```toml
name = "your-project-name"
description = "Your project description"
authors = ["Your Name <your.email@example.com>"]
```

### 3. Create Your First Subproject

```bash
./scripts/create_python_subproject.sh
```

This will prompt you for:
- Subproject name (e.g., `api`, `cli`, `core`)
- Description
- Whether to include tests (recommended: yes)

### 4. Install Dependencies

```bash
poetry install --with dev
```

## 🚀 Quick Commands

```bash
# Create new subproject
./scripts/create_python_subproject.sh

# Add library to subproject
./scripts/add_library.sh <subproject> <library>

# Fix all code issues
make lint-all

# Run all tests
make test-all
```

## 🤖 VS Code Copilot

Type these in Copilot chat:
- `/monorepo-admin` - Natural language assistant
- `/monorepo-intro` - Quick reference
- `/monorepo-create-subproject` - Create subprojects
- `/monorepo-add-library` - Add dependencies

## 📚 Resources

- [Full Template Guide](TEMPLATE_GUIDE.md) - Complete documentation
- [Scripts Documentation](TEMPLATE_GUIDE.md#-automation-scripts)
- [Troubleshooting](TEMPLATE_GUIDE.md#-support)

## 🎯 Next Steps

1. **Create subprojects** for your application components
2. **Add dependencies** as needed
3. **Set up CI/CD** if using Azure DevOps
4. **Configure pre-commit hooks**: `poetry run pre-commit install`
5. **Start coding!**

## 💡 Tips

- Use `/monorepo-admin` in Copilot for natural language help
- Keep subprojects focused on single responsibilities
- Put shared code in a `common` or `shared` subproject
- Use DevContainers for consistent development environments

---

Remember to delete this file once you're familiar with the template!