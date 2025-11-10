---
mode: "ask"
description: "Learn how to build agentic chatbots with this framework"
---

## Agentic Chatbot Framework - Quick Guide

This framework helps you build intelligent chatbots with tool-calling capabilities using Semantic Kernel or LlamaIndex in a structured, three-step workflow.

## What Are Agentic Chatbots?

**Agentic chatbots** are AI assistants that can:

- ✅ Call tools/functions to perform actions (get weather, fetch stock prices, query databases)
- ✅ Make decisions about which tools to use based on user requests
- ✅ Maintain conversation context and state
- ✅ Provide intelligent, context-aware responses

## Framework Features

- **Two AI Frameworks**: Choose between Semantic Kernel (general-purpose) or LlamaIndex (data-heavy)
- **Production-Ready**: Built-in error handling, validation, and security best practices
- **Streamlit UI**: Each agent gets a ready-to-use web interface
- **Multi-Persistence**: Support for different storage backends
- **Monorepo Structure**: Organized, isolated agent projects

## Three-Step Workflow

### Step 1: Create Agent Project

**Prompt**: `/agentic-chatbot-agent-project`

Creates complete project structure:

- Agent scaffolding (Semantic Kernel or LlamaIndex)
- Minimal auto-generated prompt
- Empty tools file (ready for Step 3)
- Streamlit web interface
- Run scripts

**Example**:

```
/agentic-chatbot-agent-project Create a weather_agent
# You'll be asked for: name, description, framework choice
```

### Step 2: Customize Agent Prompt

**Prompt**: `/agentic-chatbot-agent-prompt`

Updates the agent's system prompt to define:

- Agent role and personality
- Behavioral guidelines
- Response formatting
- Tool usage instructions

**Example**:

```
/agentic-chatbot-agent-prompt Update weather_agent to act like a professional meteorologist
```

### Step 3: Add Agent Tools

**Prompt**: `/agentic-chatbot-agent-tools`

Adds **ONE tool at a time** with:

- Complete, production-ready implementation
- Error handling and input validation
- API integration (if needed)
- Automatic registration in agent and prompt

**Example**:

```
/agentic-chatbot-agent-tools Add get_weather tool to weather_agent using OpenWeatherMap API
# Repeat this step for each additional tool
```

## Quick Start Example

Build a stock price agent in 3 steps:

```bash
# Step 1: Create project
/agentic-chatbot-agent-project Create stock_agent
# Input: "stock_agent", "Stock Price Agent", "provides stock market information", Semantic Kernel

# Step 2: Customize behavior
/agentic-chatbot-agent-prompt
# Define: "You are a professional financial assistant that provides real-time stock data..."

# Step 3: Add tools (repeat for each tool)
/agentic-chatbot-agent-tools Add get_stock_price to stock_agent using yfinance
/agentic-chatbot-agent-tools Add get_stock_info to stock_agent using yfinance
```

## Project Structure

Each agent project follows this structure:

```
{agent_name}/
├── {agent}_agent.py          # Agent implementation
├── {agent}_tools.py           # Tool functions
├── {agent}_prompt.txt         # System prompt (editable!)
├── {agent}_app.py             # Streamlit interface
└── run_app.sh                 # Launch script
```

## Running Your Agent

### Command Line (CLI)

```bash
poetry run python {agent_name}/{agent_name}_agent.py
```

### Web Interface (Streamlit)

```bash
streamlit run {agent_name}/{agent_name}_app.py
# or use the convenience script:
./{agent_name}/run_app.sh
```

### Run Tests

```bash
make test-{agent_name}
```

## Available Prompts

Use these in your AI assistant:

- `/agentic-chatbot-intro` - Show this guide
- `/agentic-chatbot-agent-project` - Create new agent project (Step 1)
- `/agentic-chatbot-agent-prompt` - Customize agent prompt (Step 2)
- `/agentic-chatbot-agent-tools` - Add tools to agent (Step 3)

## Key Concepts

### Prompts are Files

- Edit `{agent}_prompt.txt` to change agent behavior
- No code changes needed
- Changes take effect immediately (agents load prompts at runtime)

### Tools are Functions

- Simple Python functions that return strings
- Complete error handling and validation
- Environment variables for API keys (no hardcoded secrets)

### One Tool at a Time

- Add tools incrementally
- Test each tool before adding the next
- Repeat Step 3 for each new tool

### Framework Selection

**Choose Semantic Kernel when:**

- Building general-purpose agents
- Integrating with APIs and services
- Need Microsoft Azure integration
- Want straightforward tool calling

**Choose LlamaIndex when:**

- Working with large documents or datasets
- Need advanced retrieval capabilities
- Building RAG (Retrieval-Augmented Generation) applications
- Indexing and searching data

## Best Practices

### When Creating Agents

1. Start with clear requirements (what should the agent do?)
2. Choose the appropriate framework
3. Keep prompts focused (one clear role per agent)
4. Add tools incrementally

### When Writing Tools

1. Always return strings (LLMs work best with text)
2. Validate all inputs
3. Handle errors gracefully (return error messages, don't raise exceptions)
4. Use environment variables for API keys
5. Set timeouts for API calls (10 seconds recommended)

### When Customizing Prompts

1. Be specific about tool usage
2. Provide examples of good interactions
3. Set clear boundaries (what NOT to do)
4. Update prompts when adding new tools

## Essential Commands

```bash
# Create agent
/agentic-chatbot-agent-project

# Update prompt
/agentic-chatbot-agent-prompt

# Add tools (repeat as needed)
/agentic-chatbot-agent-tools

# Test agent
poetry run python {agent}_agent.py

# Run web interface
streamlit run {agent}_app.py

# Run tests
make test-{agent}

# Lint code
make lint-all
```

## Example Agents You Can Build

- **Weather Agent**: Get current weather, forecasts, alerts
- **Stock Agent**: Fetch stock prices, market data, company info
- **Database Agent**: Query databases, generate reports
- **Document Agent**: Search, summarize, analyze documents
- **API Agent**: Integrate with external services (Slack, GitHub, etc.)
- **Research Agent**: Web search, fact-checking, information gathering

## Common Workflows

### Building a Weather Agent

```
1. /agentic-chatbot-agent-project → Create weather_agent
2. /agentic-chatbot-agent-prompt → Define meteorologist persona
3. /agentic-chatbot-agent-tools → Add get_weather (OpenWeatherMap)
4. /agentic-chatbot-agent-tools → Add get_forecast
5. /agentic-chatbot-agent-tools → Add get_alerts
6. Test: poetry run python weather_agent/weather_agent_agent.py
7. Launch UI: ./weather_agent/run_app.sh
```

### Adding a Tool to Existing Agent

```
1. /agentic-chatbot-agent-tools → Specify tool name, purpose, API
2. Tool function added to {agent}_tools.py
3. Tool registered in {agent}_agent.py
4. Tool documented in {agent}_prompt.txt
5. Dependencies added automatically
6. Test immediately
```

## Tips and Tricks

- **Prompts are hot-reloadable**: Edit the .txt file and restart the agent
- **Test early, test often**: Run the agent after each tool addition
- **Use the Streamlit UI**: Visual testing is easier than CLI
- **Check dependencies**: Tools are added to the correct Poetry group automatically
- **Environment variables**: Store API keys in `.env` file (never commit it!)
- **One responsibility**: Each agent should have one clear purpose

## Repository Structure

```
project-root/
├── core/
│   ├── agents/              # Abstract base classes
│   ├── scaffolding/         # Project generation scripts
│   └── persistence/         # Storage backends
├── {agent1}/               # Your first agent
├── {agent2}/               # Your second agent
└── .github/prompts/        # Prompt files (this directory)
```

## Need Help?

- **Detailed docs**: See [.github/prompts/README.md](.github/prompts/README.md)
- **Framework docs**:
  - [Semantic Kernel](https://learn.microsoft.com/semantic-kernel/)
  - [LlamaIndex](https://docs.llamaindex.ai/)
- **Scaffolding script**: `core/scaffolding/create_agent_project.sh`

---

**Ready to build your first agent?** Start with `/agentic-chatbot-agent-project`! 🚀
