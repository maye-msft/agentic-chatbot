# Agentic Chatbot Development Prompts

This directory contains specialized prompts for building intelligent agentic chatbots using a modular, three-step workflow.

## 📖 About This Repository

This repository provides an **agentic framework** for building intelligent chatbots with tool-calling capabilities. The framework supports two powerful AI frameworks:

- **Semantic Kernel** - Microsoft's SDK for integrating AI services with conventional programming
- **LlamaIndex** - Data framework for LLM applications with advanced retrieval and reasoning

### Key Features

✅ **Multi-persistence support** - Built-in support for different storage backends
✅ **Streamlit UI** - Ready-to-use web interface for each agent
✅ **Tool-based architecture** - Modular, extensible agent capabilities
✅ **Production-ready scaffolding** - Automated project generation with best practices
✅ **Monorepo structure** - Organized codebase with isolated agent projects

### Repository Structure

```text
project-root/
├── core/
│   ├── agents/                    # Abstract base classes
│   │   ├── semantic_kernel_agent.py
│   │   └── llama_index_agent.py
│   ├── scaffolding/               # Project generation scripts
│   │   ├── create_agent_project.sh
│   │   └── templates/             # Code templates
│   └── persistence/               # Storage backends
├── {agent_name}/                  # Each agent is a separate project
│   ├── {agent}_agent.py          # Agent implementation
│   ├── {agent}_tools.py          # Tool functions
│   ├── {agent}_prompt.txt        # System prompt (runtime loaded)
│   ├── {agent}_app.py            # Streamlit interface
│   └── run_app.sh                # Launch script
└── .github/prompts/               # This directory
```

## Three-Step Workflow

### Step 1: Create Agent Project Structure

**Prompt**: [agentic-chatbot-agent-project.prompt.md](agentic-chatbot-agent-project.prompt.md)

**Purpose**: Create the basic project structure with templates and a minimal auto-generated prompt.

**What it does**:
- Collects: project name, agent name, description, tool names, framework
- Generates a minimal system prompt automatically
- Runs scaffolding script to create project structure
- Creates: agent file, Streamlit app, tools stubs, run scripts

**User provides**: Basic project metadata only

**Output**:
- `{project}/` directory with all template files
- `{project}/{project}_prompt.txt` - Minimal prompt (to be edited in Step 2)
- `{project}/{project}_tools.py` - Tool stubs (to be implemented in Step 3)

---

### Step 2: Update Agent Prompt

**Prompt**: [agentic-chatbot-agent-prompt.prompt.md](agentic-chatbot-agent-prompt.prompt.md)

**Purpose**: Customize the agent's behavior by updating the system prompt created in Step 1.

**What it does**:
- Reads existing prompt from `{project}/{project}_prompt.txt`
- Gets updated prompt content from user
- Saves updated prompt back to the file

**User provides**: Updated prompt text (or file path, or modification instructions)

**Output**:
- Updated `{project}/{project}_prompt.txt` with custom agent behavior

---

### Step 3: Add Agent Tools

**Prompt**: [agentic-chatbot-agent-tools.prompt.md](agentic-chatbot-agent-tools.prompt.md)

**Purpose**: Add **ONE tool at a time** with complete, production-ready implementation.

**What it does**:
- Collects specifications for a single tool
- Generates complete Python code with error handling, type hints, docstrings
- Adds required dependencies via `poetry add --group {project}`
- Updates agent file to register the tool
- Updates prompt file to document the tool
- Preserves existing tools in the file

**User provides**: Tool specification (name, purpose, parameters, data source, API details)

**Output**:
- Updated `{project}/{project}_tools.py` with new tool function
- Updated `{project}/{project}_agent.py` with tool registration
- Updated `{project}/{project}_prompt.txt` with tool documentation
- Dependencies added to project group in `pyproject.toml`
- List of required environment variables

**Note**: This prompt adds one tool at a time. Repeat to add more tools.

---

## 🚀 Quick Start Example

Here's how to build a complete weather agent in 3 steps:

**Step 1: Create the project**

```bash
# The prompt will collect: project name, agent name, description, framework
# Input example: weather_agent, "Weather Agent", "provides weather information", Semantic Kernel
# Output: Complete project structure with minimal prompt
```

**Step 2: Customize the prompt**

```bash
# Define agent behavior, personality, and guidelines
# Example: "You are a professional meteorologist assistant..."
# Output: Updated weather_agent/weather_agent_prompt.txt
```

**Step 3: Add tools (repeat for each tool)**

```bash
# Add get_weather tool using OpenWeatherMap API
# Output: weather_agent/weather_agent_tools.py with get_weather function
# Then repeat to add get_forecast, get_alerts, etc.
```

## 💡 Usage

### With Claude Code

Reference the prompts in your requests or use them as context:

```text
@agentic-chatbot-agent-project Create a stock_agent
```

```text
@agentic-chatbot-agent-prompt Update stock_agent to be more professional
```

```text
@agentic-chatbot-agent-tools Add get_stock_price tool to stock_agent using yfinance
```

### With GitHub Copilot

Use the `@workspace` command with the prompt files as context for your agent creation tasks.

## Workflow Example: Weather Agent

### Step 1: Create Project

```text
User: Create a weather agent with tools: get_weather, get_forecast, get_alerts

Copilot:
- Collects: name, description, framework choice
- Generates minimal prompt automatically
- Runs scaffolding script (twice)
- Creates project structure

Output: weather_agent/ directory with all files
```

### Step 2: Update Prompt

```text
User: Update the weather_agent prompt to act like a professional meteorologist

Copilot:
- Reads current prompt from weather_agent/weather_agent_prompt.txt
- Gets updated prompt from user
- Saves updated prompt

Output: Updated weather_agent/weather_agent_prompt.txt
```

### Step 3: Implement Tools

```text
User: Implement weather_agent tools using OpenWeatherMap API

Copilot:
- Generates complete code for get_weather, get_forecast, get_alerts
- Adds error handling, validation, type hints
- Adds dependency: poetry add requests --group weather_agent
- Provides API key setup instructions

Output: Complete weather_agent/weather_agent_tools.py
```

## 🎯 Design Philosophy

### Separation of Concerns

- **Prompts are files** - Edit prompts without touching code
- **Tools are functions** - Simple, testable, reusable Python functions
- **Agents are classes** - Clean abstractions over AI frameworks
- **Apps are interfaces** - UI separate from business logic

### One Thing at a Time

- Create project → Customize prompt → Add tools (one by one)
- Each prompt focuses on a single responsibility
- Clear, incremental progress
- Easy to test at each step

### Production-Ready from Start

- Comprehensive error handling
- Input validation
- Environment variable management
- Timeout configuration for API calls
- Security best practices (no hardcoded secrets)

## ✅ Benefits of This Approach

1. **Clear separation**: Setup → Prompt → Tools (no mixed concerns)
2. **Iterative**: Each step can be repeated independently
3. **User control**: You provide key content (prompt, tool specs)
4. **Template-based**: Consistent, maintainable project structure
5. **Production-ready**: Complete implementations with proper error handling
6. **Framework flexibility**: Choose Semantic Kernel or LlamaIndex
7. **Incremental tools**: Add one tool at a time, fully tested

## File Locations

All prompts created by this workflow follow this structure:

```text
{project_name}/
├── {project_name}_prompt.txt          # Step 1 creates, Step 2 updates
├── {project_name}_tools.py            # Step 1 creates stubs, Step 3 implements
├── {project_name}_agent.py            # Step 1 creates from template
├── {project_name}_app.py              # Step 1 creates from template
├── run_app.sh                         # Step 1 creates from template
├── __init__.py                        # Step 1 creates from template
└── tests/                             # Step 1 creates from template
```

## 🎓 Best Practices

### When Creating Agents

1. **Start with clear requirements** - What should the agent do? Who is it for?
2. **Choose the right framework**:
   - Semantic Kernel for general-purpose agents and API integrations
   - LlamaIndex for data-heavy tasks with retrieval and indexing needs
3. **Keep prompts focused** - One clear role per agent
4. **Add tools incrementally** - One at a time, fully tested before adding the next

### When Writing Tools

1. **Always return strings** - LLMs work best with text responses
2. **Validate all inputs** - Check for missing, empty, or invalid data
3. **Handle errors gracefully** - Return error messages, don't raise exceptions
4. **Use environment variables** - Never hardcode API keys or secrets
5. **Set timeouts** - Prevent hanging on slow API calls (10 seconds recommended)
6. **Document thoroughly** - Clear docstrings help both humans and LLMs understand tools

### When Customizing Prompts

1. Be specific about tool usage patterns
2. Provide examples of good interactions
3. Set clear boundaries (what NOT to do)
4. Update prompts whenever you add new tools
5. Keep prompts concise but comprehensive

## 📚 Additional Resources

### Framework Documentation

- [Semantic Kernel Docs](https://learn.microsoft.com/semantic-kernel/)
- [LlamaIndex Docs](https://docs.llamaindex.ai/)

### Project Setup

- See main [README.md](../../README.md) for development setup
- Review `core/scaffolding/create_agent_project.sh` to understand project generation

## 🤝 Contributing

When adding new prompts or improving existing ones:

1. Follow the established three-step pattern
2. Use the frontmatter format (`mode: 'agent'`, `description: '...'`)
3. Include clear examples
4. Test with actual agent creation
5. Update this README if needed

## ⚡ Tips and Tricks

- **Reuse prompts**: The tool-adding prompt is designed for multiple invocations
- **Test early**: Run `poetry run python {agent}_agent.py` after each step
- **Use the UI**: Launch Streamlit apps to visually test your agents
- **Check dependencies**: Add packages to the correct Poetry group (`--group {project}`)
- **Review prompts**: Agent behavior comes from the prompt file - edit it freely
- **No code restart needed**: Agents load prompts from files at runtime

---

**Happy building!** 🚀

*These prompts are designed to work seamlessly with the agentic chatbot framework. For issues or suggestions, please open an issue in the repository.*
