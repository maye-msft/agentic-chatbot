#!/bin/bash

# Helper script to save agent prompt to the project directory
# Usage: cat << 'EOF' | ./core/scaffolding/save_prompt.sh <project_name>
# Your prompt content here...
# EOF

set -e

if [ -z "$1" ]; then
    echo "Usage: cat << 'EOF' | $0 <project_name>"
    echo "Your prompt content..."
    echo "EOF"
    echo ""
    echo "Example: cat << 'EOF' | $0 weather_agent"
    echo "You are a helpful weather agent..."
    echo "EOF"
    exit 1
fi

PROJECT_NAME="$1"

# Get root directory (two levels up from core/scaffolding/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Define the prompt file path in the project directory
PROJECT_DIR="${ROOT_DIR}/${PROJECT_NAME}"
PROMPT_FILE="${PROJECT_DIR}/${PROJECT_NAME}_prompt.txt"

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Error: Project directory not found: $PROJECT_DIR"
    echo ""
    echo "Please create the project first by running:"
    echo "  ./core/scaffolding/create_agent_project.sh"
    echo ""
    exit 1
fi

echo "📝 Saving prompt for: $PROJECT_NAME"
echo "📁 Location: $PROMPT_FILE"
echo ""

# Read from stdin and save to file
cat > "$PROMPT_FILE"

echo ""
echo "✅ Prompt saved successfully!"
echo "📍 File: $PROMPT_FILE"
