---
mode: 'agent'
description: 'Step 1: Create a new agentic chatbot project'
---

# Create Agent Project

Create a new agentic chatbot project with basic structure and hello world placeholders.

## Instructions

1. **Collect information from user:**
   - Project name (e.g., `weather_agent`, `stock_agent`)
   - Agent name (e.g., "Weather Agent")
   - Agent description
   - Framework: 1 for Semantic Kernel, 2 for LlamaIndex (default: 1)

2. **Run scaffolding script:**
   ```bash
   echo -e "{project}\n{agent_name}\n{description}\n\n{framework}" | ./core/scaffolding/create_agent_project.sh
   ```

   Note: Use empty string for tools (`\n\n`)

   The script will:
   - Create project folder structure
   - Auto-generate a minimal prompt
   - Create agent file from template (with no tools)
   - Create Streamlit app from template
   - Create empty tools file
   - Create run scripts

3. **Inform user:**
   ```
   ✅ Project '{project}' created!

   📁 Files created:
     - {project}/{project}_prompt.txt (minimal - edit in Step 2)
     - {project}/{project}_tools.py (empty - add tools in Step 3)
     - {project}/{project}_agent.py (from template)
     - {project}/{project}_app.py (Streamlit from template)
     - {project}/run_app.sh

   🚀 Next steps:
     Step 2: Update agent prompt
     Step 3: Add and implement tools
   ```

## Notes

- Single script run creates everything
- Minimal prompt is auto-generated
- Tools file is empty (no tools yet)
- Agent loads prompt from file at runtime
- Update prompt in Step 2, add tools in Step 3
