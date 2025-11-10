#!/bin/bash

# Script to create a new agent project with tools and Streamlit app
# Usage: ./core/scaffolding/create_agent_project.sh

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/templates"
PROMPTS_DIR="$SCRIPT_DIR/prompts"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Collect user inputs
read -p "Enter the project name (e.g., weather_agent): " PROJECT_NAME

# Process project name
PROJECT_NAME=$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | tr ' -' '__')

# Collect other inputs
read -p "Enter the agent name (e.g., Weather Agent): " AGENT_NAME
read -p "Enter the agent description: " AGENT_DESCRIPTION
read -p "Enter tool names (comma-separated, e.g., get_weather,get_forecast): " TOOL_NAMES_INPUT
read -p "Choose framework - 1 for Semantic Kernel, 2 for LlamaIndex (1/2): " FRAMEWORK_CHOICE

# Convert tool names to array
IFS=',' read -ra TOOL_NAMES <<< "$TOOL_NAMES_INPUT"

# Determine agent framework
if [ "$FRAMEWORK_CHOICE" == "1" ]; then
    AGENT_TYPE="semantic_kernel"
    AGENT_CLASS_SUFFIX="SemanticKernelAgent"
    AGENT_BASE_CLASS="AbstractSemanticKernelAgent"
    AGENT_IMPORT="from core.agents.semantic_kernel_agent import AbstractSemanticKernelAgent"
    AGENT_TEMPLATE="$TEMPLATE_DIR/agent_semantic_kernel.py.tpl"
else
    AGENT_TYPE="llama_index"
    AGENT_CLASS_SUFFIX="LlamaIndexAgent"
    AGENT_BASE_CLASS="AbstractLlamaIndexAgent"
    AGENT_IMPORT="from core.agents.llama_index_agent import AbstractLlamaIndexAgent"
    AGENT_TEMPLATE="$TEMPLATE_DIR/agent_llama_index.py.tpl"
fi

# Convert project name to class name (e.g., weather_agent -> WeatherAgent)
AGENT_CLASS_NAME=$(echo "$PROJECT_NAME" | sed -r 's/(^|_)([a-z])/\U\2/g')${AGENT_CLASS_SUFFIX}
AGENT_ID="${PROJECT_NAME}_${AGENT_TYPE}_agent"

echo ""
echo "Creating agent project with the following configuration:"
echo "  Project Name: $PROJECT_NAME"
echo "  Agent Name: $AGENT_NAME"
echo "  Agent Class: $AGENT_CLASS_NAME"
echo "  Agent ID: $AGENT_ID"
echo "  Agent Framework: $AGENT_TYPE"
echo "  Tools: ${TOOL_NAMES[@]}"
echo ""

# Step 1: Create the subproject using the existing script
echo "Step 1: Creating Python subproject..."
cd "$ROOT_DIR"
echo -e "${PROJECT_NAME}\n${AGENT_DESCRIPTION}\ny" | ./scripts/create_python_subproject.sh

# Step 2: Remove the default hello_world.py file
echo "Step 2: Removing default files..."
rm -f "${ROOT_DIR}/${PROJECT_NAME}/hello_world.py"

# Step 3: Check for prompt file in project directory
echo "Step 3: Checking for agent prompt file..."
PROMPT_FILE="${ROOT_DIR}/${PROJECT_NAME}/${PROJECT_NAME}_prompt.txt"

if [ ! -f "$PROMPT_FILE" ]; then
    echo "📝 Prompt file not found. Generating minimal prompt..."

    # Generate minimal prompt automatically
    MINIMAL_PROMPT="You are a helpful ${AGENT_NAME} that ${AGENT_DESCRIPTION}.

## Your Capabilities
You have access to the following tools:"

    # Add each tool to the prompt
    for TOOL_NAME in "${TOOL_NAMES[@]}"; do
        TOOL_NAME=$(echo "$TOOL_NAME" | xargs)
        TOOL_TITLE=$(echo "$TOOL_NAME" | sed -e "s/\b\(.\)/\u\1/g")
        MINIMAL_PROMPT+="
- ${TOOL_NAME}: ${TOOL_TITLE} tool"
    done

    MINIMAL_PROMPT+="

## Guidelines
- Use the available tools to accomplish tasks
- Provide clear and helpful responses
- Ask for clarification when needed"

    # Save the minimal prompt
    echo "$MINIMAL_PROMPT" > "$PROMPT_FILE"
    echo "✅ Generated minimal prompt at: $PROMPT_FILE"
    echo ""
fi

# Read the agent prompt from file
AGENT_PROMPT=$(cat "$PROMPT_FILE")
echo "✅ Using prompt file: $PROMPT_FILE"
echo ""

# Step 4: Create tools file from template
echo "Step 4: Creating tools file..."
TOOLS_FILE="${ROOT_DIR}/${PROJECT_NAME}/${PROJECT_NAME}_tools.py"

# Generate tools code using the tool function template
TOOLS_CODE=""
for TOOL_NAME in "${TOOL_NAMES[@]}"; do
    # Trim whitespace
    TOOL_NAME=$(echo "$TOOL_NAME" | xargs)

    # Convert to snake_case function name
    FUNC_NAME=$(echo "$TOOL_NAME" | tr '[:upper:]' '[:lower:]' | tr ' -' '__')

    # Convert to Title Case for description
    TOOL_TITLE=$(echo "$TOOL_NAME" | sed -e "s/\b\(.\)/\u\1/g")

    # Read the tool function template and substitute variables
    TOOL_FUNC=$(sed "s/{{FUNC_NAME}}/$FUNC_NAME/g; s/{{TOOL_TITLE}}/$TOOL_TITLE/g" "$TEMPLATE_DIR/tool_function.tpl")

    TOOLS_CODE+="$TOOL_FUNC


"
done

# Create the tools file using the tools template
sed "s/{{AGENT_NAME}}/$AGENT_NAME/g" "$TEMPLATE_DIR/agent_tools.py.tpl" | \
    awk -v tools="$TOOLS_CODE" '{gsub(/{{TOOLS_CODE}}/, tools); print}' > "$TOOLS_FILE"

# Step 5: Create agent file from template
echo "Step 5: Creating agent file..."
AGENT_FILE="${ROOT_DIR}/${PROJECT_NAME}/${PROJECT_NAME}_agent.py"

# Generate tool imports
TOOL_IMPORTS=""
TOOL_DICT=""
for TOOL_NAME in "${TOOL_NAMES[@]}"; do
    TOOL_NAME=$(echo "$TOOL_NAME" | xargs)
    FUNC_NAME=$(echo "$TOOL_NAME" | tr '[:upper:]' '[:lower:]' | tr ' -' '__')
    TOOL_TITLE=$(echo "$TOOL_NAME" | sed -e "s/\b\(.\)/\u\1/g")

    if [ -z "$TOOL_IMPORTS" ]; then
        TOOL_IMPORTS="$FUNC_NAME"
    else
        TOOL_IMPORTS="$TOOL_IMPORTS, $FUNC_NAME"
    fi

    TOOL_DICT+="                \"${TOOL_TITLE}\": AbstractTool(
                    name=\"${TOOL_TITLE}\",
                    description=\"${TOOL_TITLE} tool\",
                    function=${FUNC_NAME}
                ),
"
done

# Remove trailing comma and newline from TOOL_DICT
TOOL_DICT=$(echo "$TOOL_DICT" | sed '$ s/,$//')

# Escape special characters for sed
AGENT_DESCRIPTION_ESCAPED=$(echo "$AGENT_DESCRIPTION" | sed 's/[&/\]/\\&/g')
TOOL_DICT_ESCAPED=$(echo "$TOOL_DICT" | sed 's/[&/\]/\\&/g')
TOOL_IMPORTS_ESCAPED=$(echo "$TOOL_IMPORTS" | sed 's/[&/\]/\\&/g')

# Create the agent file using the appropriate template
# Note: Agent now loads prompt from file, so no need to substitute {{AGENT_PROMPT}}
awk -v tool_dict="$TOOL_DICT" '{gsub(/{{TOOL_DICT}}/, tool_dict); print}' "$AGENT_TEMPLATE" | \
    sed "s/{{PROJECT_NAME}}/$PROJECT_NAME/g; \
         s/{{AGENT_NAME}}/$AGENT_NAME/g; \
         s/{{AGENT_CLASS_NAME}}/$AGENT_CLASS_NAME/g; \
         s/{{AGENT_ID}}/$AGENT_ID/g; \
         s/{{AGENT_DESCRIPTION}}/$AGENT_DESCRIPTION_ESCAPED/g; \
         s/{{TOOL_IMPORTS}}/$TOOL_IMPORTS_ESCAPED/g" > "$AGENT_FILE"

# Step 6: Create Streamlit app file from template
echo "Step 6: Creating Streamlit app file..."
APP_FILE="${ROOT_DIR}/${PROJECT_NAME}/${PROJECT_NAME}_app.py"

sed "s/{{PROJECT_NAME}}/$PROJECT_NAME/g; \
     s/{{AGENT_NAME}}/$AGENT_NAME/g; \
     s/{{AGENT_CLASS_NAME}}/$AGENT_CLASS_NAME/g; \
     s/{{AGENT_ID}}/$AGENT_ID/g" "$TEMPLATE_DIR/agent_app.py.tpl" > "$APP_FILE"

# Step 7: Create run script from template
echo "Step 7: Creating run script..."
RUN_SCRIPT="${ROOT_DIR}/${PROJECT_NAME}/run_app.sh"

sed "s/{{PROJECT_NAME}}/$PROJECT_NAME/g; \
     s/{{AGENT_NAME}}/$AGENT_NAME/g" "$TEMPLATE_DIR/run_app.sh.tpl" > "$RUN_SCRIPT"
chmod +x "$RUN_SCRIPT"

# Step 8: Update __init__.py from template
echo "Step 8: Updating __init__.py..."
INIT_FILE="${ROOT_DIR}/${PROJECT_NAME}/__init__.py"

sed "s/{{PROJECT_NAME}}/$PROJECT_NAME/g; \
     s/{{AGENT_NAME}}/$AGENT_NAME/g; \
     s/{{AGENT_CLASS_NAME}}/$AGENT_CLASS_NAME/g" "$TEMPLATE_DIR/__init__.py.tpl" > "$INIT_FILE"

echo ""
echo "✅ Agent project '${PROJECT_NAME}' created successfully!"
echo ""
echo "📁 Created files:"
echo "  - ${PROJECT_NAME}/${PROJECT_NAME}_prompt.txt (Agent system prompt)"
echo "  - ${PROJECT_NAME}/${PROJECT_NAME}_tools.py (${#TOOL_NAMES[@]} tools)"
echo "  - ${PROJECT_NAME}/${PROJECT_NAME}_agent.py (${AGENT_CLASS_NAME})"
echo "  - ${PROJECT_NAME}/${PROJECT_NAME}_app.py (Streamlit app)"
echo "  - ${PROJECT_NAME}/run_app.sh (Run script)"
echo "  - ${PROJECT_NAME}/__init__.py"
echo ""
echo "🚀 Next steps:"
echo "  1. Review and implement tool logic in: ${PROJECT_NAME}/${PROJECT_NAME}_tools.py"
echo "  2. Test the agent: poetry run python ${PROJECT_NAME}/${PROJECT_NAME}_agent.py"
echo "  3. Run the Streamlit app: streamlit run ${PROJECT_NAME}/${PROJECT_NAME}_app.py"
echo "     or use: ./${PROJECT_NAME}/run_app.sh"
echo "  4. Run tests: make test-${PROJECT_NAME}"
echo ""
echo "💡 The agent prompt, tools, and app are ready for customization!"
