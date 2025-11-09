#!/bin/bash

# Script to create a new Python subproject in the monorepo
# Usage: ./create_python_subproject.sh

set -e

read -p "Enter the subproject name (e.g. python_new_project): " SUBPROJECT
read -p "Enter a short description: " DESCRIPTION
read -p "Add tests? (y/n): " ADD_TESTS

# Paths
ROOT_DIR="."
PROJECT_DIR="$ROOT_DIR/$SUBPROJECT"
DEVCONTAINER_DEST="$ROOT_DIR/.devcontainer/$SUBPROJECT"
PYPROJECT_TOML="$ROOT_DIR/pyproject.toml"
QA_PIPELINE="$ROOT_DIR/.azuredevops/qa_pipeline.yaml"
MAKEFILE="$ROOT_DIR/Makefile"
TEMPLATE_DIR="$ROOT_DIR/scripts/python_templates"
ADD_TESTS=$(echo "$ADD_TESTS" | tr '[:upper:]' '[:lower:]')

# 1. Create the new subproject folder
mkdir -p "$PROJECT_DIR"

# 2. create a init.py file
if [ ! -f "$PROJECT_DIR/__init__.py" ]; then
    touch "$PROJECT_DIR/__init__.py"
fi

# 3. Create a hello_world.py file from template
sed "s/{{SUBPROJECT}}/$SUBPROJECT/g; s/{{DESCRIPTION}}/$DESCRIPTION/g" \
    "$TEMPLATE_DIR/hello_world.py.tpl" > "$PROJECT_DIR/hello_world.py"

# 4. Add tests if requested
if [ "$ADD_TESTS" == "y" ]; then
    # 4a. Create a test directory and test file
    mkdir -p "$PROJECT_DIR/tests"
    cp "$TEMPLATE_DIR/test_sample.py.tpl" "$PROJECT_DIR/tests/test_sample.py"

    # 4b. Add a test script in the Makefile
    if ! grep -q "test-$SUBPROJECT:" "$ROOT_DIR/Makefile"; then
        echo -e "\n\ntest-$SUBPROJECT:\n\tpoetry run pytest $SUBPROJECT/tests" >> "$ROOT_DIR/Makefile"
    fi
    if ! grep -q "test-$SUBPROJECT-coverage:" "$MAKEFILE"; then
        echo -e "\ntest-$SUBPROJECT-coverage:\n\tpoetry run pytest --disable-warnings --maxfail=1 --cov=$SUBPROJECT $SUBPROJECT/tests" >> "$MAKEFILE"
    fi

    # 4c. Add tests to qa pipelines
    if ! grep -q "Run $SUBPROJECT tests" "$QA_PIPELINE"; then
        echo -e "\n  - script: |" >> "$QA_PIPELINE"
        echo -e "      make test-$SUBPROJECT-coverage" >> "$QA_PIPELINE"
        echo -e "    displayName: \"Run $SUBPROJECT tests\"" >> "$QA_PIPELINE"
    fi
fi

# 5. Update pyproject.toml with a new group (if poetry is used)
if grep -q '\[tool.poetry\]' "$PYPROJECT_TOML"; then
    # Add a new group for the subproject if not present
    if ! grep -q "\[tool.poetry.group.$SUBPROJECT.dependencies\]" "$PYPROJECT_TOML"; then
        echo -e "\n\n[tool.poetry.group.$SUBPROJECT.dependencies]" >> "$PYPROJECT_TOML"
    fi
    if ! grep -q "\[tool.poetry.group.$SUBPROJECT\]" "$PYPROJECT_TOML"; then
        echo -e "\n[tool.poetry.group.$SUBPROJECT]\noptional = true" >> "$PYPROJECT_TOML"
    fi
fi

# 6. Create a minimal devcontainer configuration from template
mkdir -p "$DEVCONTAINER_DEST"
sed "s/{{SUBPROJECT}}/$SUBPROJECT/g" \
    "$TEMPLATE_DIR/devcontainer.json.tpl" > "$DEVCONTAINER_DEST/devcontainer.json"

# 6b. Create a Dockerfile in the devcontainer folder from template
sed "s/{{SUBPROJECT}}/$SUBPROJECT/g" \
    "$TEMPLATE_DIR/Dockerfile.tpl" > "$DEVCONTAINER_DEST/Dockerfile"

echo "✅ Python subproject '$SUBPROJECT' created successfully!"
echo "- Location: $PROJECT_DIR"
echo "- Devcontainer: $DEVCONTAINER_DEST"
echo "- Hello world: $PROJECT_DIR/hello_world.py"
if [ "$ADD_TESTS" == "y" ]; then
    echo "- Tests: $PROJECT_DIR/tests/test_sample.py"
    echo "- Makefile updated with test targets"
    echo "- QA pipeline updated with test step"
fi
echo "- pyproject.toml updated (if Poetry is used)"
