---
mode: 'agent'
description: 'Step 2: Customize the agent system prompt'
---

# Update Agent Prompt

Customize the agent's behavior by updating its system prompt file.

## Instructions

1. **Collect information from user:**
   - Project name (e.g., `weather_agent`, `stock_agent`)
   - Prompt requirements:
     - Agent role and personality
     - Capabilities description
     - Behavior guidelines
     - Response format (optional)
     - Examples (optional)

2. **Generate the prompt content:**

   Structure:
   ```
   You are a [role] that [purpose].

   ## Your Capabilities
   [Describe what the agent can do]
   [List tools if they exist, or note "Tools will be added in Step 3"]

   ## Guidelines
   - [How to use tools]
   - [How to format responses]
   - [When to ask for clarification]
   - [Any constraints or rules]

   ## Response Format (optional)
   [How to structure outputs]

   ## Examples (optional)
   User: [Example question]
   Assistant: [Example response]
   ```

3. **Save the prompt:**
   ```bash
   cat << 'EOF' | ./core/scaffolding/save_prompt.sh {project_name}
   {generated_prompt_content}
   EOF
   ```

4. **Inform user:**
   ```
   ✅ Agent prompt updated!

   📝 File: {project}/{project}_prompt.txt

   🚀 Test: poetry run python {project}/{project}_agent.py

   💡 Changes take effect immediately!
   ```

## Notes

- Agent loads prompt from file at runtime
- No code changes needed
- Can update multiple times
- Keep prompts clear and focused
