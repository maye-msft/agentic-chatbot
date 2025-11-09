#!/bin/bash

# Script to add a library to a specific subproject using Poetry
# Usage: ./add_library.sh <subproject> <library> [version]
# Example: ./add_library.sh my_api requests
# Example: ./add_library.sh my_dashboard streamlit "1.28.0"

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_error() {
    echo -e "${RED}❌ Error: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if at least 2 arguments are provided
if [ $# -lt 2 ]; then
    print_error "Insufficient arguments"
    echo "Usage: $0 <subproject> <library> [version]"
    echo "Examples:"
    echo "  $0 my_api requests"
    echo "  $0 my_dashboard streamlit 1.28.0"
    echo ""
    echo "Available subprojects:"
    # List all directories that have a corresponding poetry group
    if [ -f "pyproject.toml" ]; then
        grep -o '\[tool\.poetry\.group\.[^]]*' pyproject.toml | sed 's/\[tool\.poetry\.group\./  - /g' | grep -v "^\s*-\s*dev"
    fi
    exit 1
fi

SUBPROJECT=$1
LIBRARY=$2
VERSION=${3:-""}  # Optional version

# Paths
ROOT_DIR="."
PROJECT_DIR="$ROOT_DIR/$SUBPROJECT"
PYPROJECT_TOML="$ROOT_DIR/pyproject.toml"

# Check if subproject directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    print_error "Subproject directory '$PROJECT_DIR' does not exist"
    echo "Please create the subproject first using: ./scripts/create_python_subproject.sh"
    exit 1
fi

# Check if pyproject.toml exists
if [ ! -f "$PYPROJECT_TOML" ]; then
    print_error "pyproject.toml not found in the root directory"
    exit 1
fi

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    print_error "Poetry is not installed. Please install Poetry first."
    echo "Visit: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Check if the subproject has a poetry group
if ! grep -q "\[tool.poetry.group.$SUBPROJECT\]" "$PYPROJECT_TOML"; then
    print_error "No Poetry group found for subproject '$SUBPROJECT'"
    echo "The subproject may not have been properly initialized."
    echo ""
    echo "To fix this, add the following to pyproject.toml:"
    echo "[tool.poetry.group.$SUBPROJECT]"
    echo "optional = true"
    echo ""
    echo "[tool.poetry.group.$SUBPROJECT.dependencies]"
    exit 1
fi

# Build the poetry add command
if [ -z "$VERSION" ]; then
    print_info "Adding $LIBRARY to $SUBPROJECT group (latest version)..."
    poetry add "$LIBRARY" --group "$SUBPROJECT"
else
    print_info "Adding $LIBRARY version $VERSION to $SUBPROJECT group..."
    poetry add "$LIBRARY@$VERSION" --group "$SUBPROJECT"
fi

# Check if the command was successful
if [ $? -eq 0 ]; then
    print_success "Successfully added $LIBRARY to $SUBPROJECT!"
    echo ""
    echo "Next steps:"
    echo "1. Open the project in the $SUBPROJECT DevContainer"
    echo "2. The library will be automatically available"
    echo "3. Import it in your code: import $LIBRARY"
    echo ""
    echo "To install all dependencies for $SUBPROJECT:"
    echo "  poetry install --with $SUBPROJECT"
else
    print_error "Failed to add $LIBRARY to $SUBPROJECT"
    exit 1
fi