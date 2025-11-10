# Agentic Chatbot Framework

A production-ready framework for building intelligent chatbots with tool-calling capabilities using **Semantic Kernel** or **LlamaIndex**. This framework provides a modular, extensible architecture for creating AI agents that can perform actions, maintain conversation context, and integrate with external services.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Building Your First Agent](#building-your-first-agent)
- [Project Structure](#project-structure)
- [AI Framework Support](#ai-framework-support)
- [Persistence Strategies](#persistence-strategies)
- [GitHub Copilot Prompts](#github-copilot-prompts)
- [Development](#development)
- [Testing](#testing)
- [Environment Configuration](#environment-configuration)
- [Examples](#examples)
- [Best Practices](#best-practices)
- [Contributing](#contributing)
- [License](#license)

## Overview

This repository provides an **agentic framework** for building intelligent chatbots with tool-calling capabilities. The framework supports two powerful AI frameworks and includes production-ready features like multi-persistence support, Streamlit UI, comprehensive error handling, and automated scaffolding for rapid development.

### What Are Agentic Chatbots?

**Agentic chatbots** are AI assistants that can:

- Call tools/functions to perform actions (get weather, fetch stock prices, query databases)
- Make intelligent decisions about which tools to use based on user requests
- Maintain conversation context and state across interactions
- Provide context-aware, intelligent responses

## Key Features

- **Multi-Framework Support** - Choose between Semantic Kernel (general-purpose) or LlamaIndex (data-heavy)
- **Production-Ready** - Built-in error handling, input validation, and security best practices
- **Streamlit UI** - Each agent gets a ready-to-use web interface with conversation history
- **Multi-Persistence** - Support for in-memory, JSON file, and Azure Cosmos DB storage
- **Tool-Based Architecture** - Modular, extensible agent capabilities
- **Automated Scaffolding** - Generate complete agent projects with a single command
- **Monorepo Structure** - Organized codebase with isolated agent projects
- **OpenTelemetry Integration** - Built-in observability and tracing
- **Conversation Management** - Advanced conversation service with message history pruning
- **Type Safety** - Full type hints and mypy validation

## Architecture

The framework follows a clean, layered architecture:

```text
┌─────────────────────────────────────────────┐
│           Streamlit UI / CLI                │
├─────────────────────────────────────────────┤
│        Conversation Service Layer           │
├─────────────────────────────────────────────┤
│         Agent Abstraction Layer             │
│  ┌──────────────────┬──────────────────┐   │
│  │ Semantic Kernel  │  LlamaIndex      │   │
│  │     Agent        │     Agent        │   │
│  └──────────────────┴──────────────────┘   │
├─────────────────────────────────────────────┤
│              Tools Layer                    │
│   (User-defined functions with metadata)   │
├─────────────────────────────────────────────┤
│         Persistence Strategy Layer          │
│  ┌────────┬─────────────┬──────────────┐   │
│  │In-Mem  │ JSON File   │  Cosmos DB   │   │
│  └────────┴─────────────┴──────────────┘   │
├─────────────────────────────────────────────┤
│    Observability (OpenTelemetry)           │
└─────────────────────────────────────────────┘
```

### Core Components

1. **Abstract Agent** - Base interface for all agents ([core/agents/abstract_agent.py](core/agents/abstract_agent.py))
2. **Semantic Kernel Agent** - Microsoft's SDK integration ([core/agents/semantic_kernel_agent.py](core/agents/semantic_kernel_agent.py))
3. **LlamaIndex Agent** - Data-focused agent implementation ([core/agents/llama_index_agent.py](core/agents/llama_index_agent.py))
4. **Conversation Service** - Manages conversations and persistence ([core/conversation_service.py](core/conversation_service.py))
5. **Persistence Strategies** - Multiple storage backends ([core/persistence/](core/persistence/))
6. **Scaffolding Tools** - Automated project generation ([core/scaffolding/](core/scaffolding/))

## Quick Start

### Prerequisites

- Python 3.10+
- Poetry (for dependency management)
- Azure OpenAI API access or OpenAI API key
- Docker (optional, for DevContainers)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd <repository-name>

# Install dependencies
poetry install --with dev,core

# Set up environment variables
cp .env.example .env
# Edit .env with your Azure OpenAI or OpenAI credentials
```

### Environment Setup

Create a `.env` file in the root directory:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_BASE_URL=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002
AZURE_OPENAI_EMBEDDING_ENDPOINT=https://your-resource.openai.azure.com/

# Environment (local, demo, or sandbox)
ENVIRONMENT=local
```

## Building Your First Agent

The framework provides a **three-step workflow** for creating agents:

### Step 1: Create Agent Project

Use the scaffolding script to generate a complete agent project:

```bash
./core/scaffolding/create_agent_project.sh
```

You'll be prompted for:

- Project name (e.g., `weather_agent`)
- Agent name (e.g., "Weather Agent")
- Agent description
- Tool names (comma-separated)
- Framework choice (1 for Semantic Kernel, 2 for LlamaIndex)

**Output:**

- Complete project structure
- Auto-generated minimal prompt
- Tool stubs ready for implementation
- Streamlit web interface
- Run scripts

### Step 2: Customize Agent Prompt

Edit the generated prompt file to define your agent's behavior:

```bash
# Edit the prompt file
nano {project_name}/{project_name}_prompt.txt
```

The prompt file defines:

- Agent role and personality
- Tool usage guidelines
- Response formatting
- Behavioral rules

### Step 3: Implement Tools

Add functionality to your tools in the tools file:

```bash
# Edit the tools file
nano {project_name}/{project_name}_tools.py
```

Each tool is a Python function that:

- Takes typed parameters
- Returns a string (LLM-friendly)
- Includes error handling
- Uses environment variables for secrets

### Example: Weather Agent

```bash
# Step 1: Create project
./core/scaffolding/create_agent_project.sh
# Input: weather_agent, "Weather Agent", "provides weather information", "get_weather,get_forecast", 1

# Step 2: Customize prompt (edit weather_agent/weather_agent_prompt.txt)

# Step 3: Implement tools (edit weather_agent/weather_agent_tools.py)

# Test the agent
poetry run python weather_agent/weather_agent_agent.py

# Run the web interface
streamlit run weather_agent/weather_agent_app.py
```

## Project Structure

```text
agentic-chatbot-framework/
├── core/                           # Core framework code
│   ├── agents/                     # Agent implementations
│   │   ├── abstract_agent.py      # Base agent interface
│   │   ├── semantic_kernel_agent.py
│   │   └── llama_index_agent.py
│   ├── persistence/                # Storage strategies
│   │   ├── in_memory_persistence_strategy.py
│   │   ├── json_file_persistence_strategy.py
│   │   └── cosmosdb_persistence_strategy.py
│   ├── scaffolding/                # Project generation
│   │   ├── create_agent_project.sh
│   │   ├── save_prompt.sh
│   │   └── templates/              # Code templates
│   ├── tools/                      # Tool utilities
│   ├── common/                     # Shared types and utilities
│   ├── trace/                      # OpenTelemetry configuration
│   ├── conversation_service.py     # Conversation management
│   ├── streamlit_app.py           # Reusable Streamlit UI
│   ├── examples/                   # Example implementations
│   └── tests/                      # Core framework tests
│
├── {agent_name}/                   # Generated agent projects
│   ├── {agent}_agent.py           # Agent implementation
│   ├── {agent}_tools.py           # Tool functions
│   ├── {agent}_prompt.txt         # System prompt (editable!)
│   ├── {agent}_app.py             # Streamlit interface
│   ├── run_app.sh                 # Launch script
│   ├── __init__.py
│   └── tests/                      # Agent-specific tests
│
├── .github/
│   └── prompts/                    # GitHub Copilot prompts
│       ├── README.md               # Prompt documentation
│       ├── agentic-chatbot-intro.prompt.md
│       ├── agentic-chatbot-agent-project.prompt.md
│       ├── agentic-chatbot-agent-prompt.prompt.md
│       └── agentic-chatbot-agent-tools.prompt.md
│
├── scripts/                        # Utility scripts
├── .devcontainer/                  # Development containers
├── pyproject.toml                  # Dependencies and configuration
├── Makefile                        # Development commands
└── README.md                       # This file
```

## AI Framework Support

### Semantic Kernel

**Best for:**

- General-purpose agents
- API integrations
- Service orchestration
- Microsoft Azure integration
- Straightforward tool calling

**Features:**

- Native Azure OpenAI support
- Automatic function calling
- Plugin architecture
- Chat history management

### LlamaIndex

**Best for:**

- Document-heavy applications
- Data retrieval and indexing
- RAG (Retrieval-Augmented Generation)
- Advanced query processing
- Knowledge base integration

**Features:**

- Document indexing and retrieval
- Multiple embedding strategies
- Query engines
- ReAct agent pattern

## Persistence Strategies

The framework supports three persistence strategies:

### In-Memory Persistence

```python
from core.persistence import InMemoryPersistenceStrategy

persistence = InMemoryPersistenceStrategy()
```

**Use case:** Development, testing, temporary conversations

### JSON File Persistence

```python
from core.persistence import JSONFilePersistenceStrategy

persistence = JSONFilePersistenceStrategy(
    base_path="./conversations"
)
```

**Use case:** Local development, simple deployments, file-based storage

### Cosmos DB Persistence

```python
from core.persistence import CosmosDBPersistenceStrategy

persistence = CosmosDBPersistenceStrategy(
    cosmos_endpoint="https://...",
    cosmos_key="...",
    database_name="chatbot",
    container_name="conversations"
)
```

**Use case:** Production deployments, multi-user systems, cloud-native applications

## GitHub Copilot Prompts

This repository includes specialized GitHub Copilot prompts for building agents with a structured, three-step workflow. See [.github/prompts/README.md](.github/prompts/README.md) for details.

### Available Prompts

- **agentic-chatbot-intro** - Quick reference guide
- **agentic-chatbot-agent-project** - Create new agent project (Step 1)
- **agentic-chatbot-agent-prompt** - Customize agent prompt (Step 2)
- **agentic-chatbot-agent-tools** - Add tools to agent (Step 3)

### Usage with AI Assistants

```text
# With Claude Code
@agentic-chatbot-agent-project Create a stock_agent

# With GitHub Copilot
Use @workspace with prompt files as context
```

## Development

### Code Quality

```bash
# Format code
make lint-all

# Check code quality
make check-all

# Run all tests
make test-all

# Run specific agent tests
make test-{agent_name}

# Run with coverage
make test-{agent_name}-coverage
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
poetry run pre-commit install

# Run manually
poetry run pre-commit run --all-files
```

### Creating a New Agent

```bash
# Method 1: Using scaffolding script
./core/scaffolding/create_agent_project.sh

# Method 2: Using GitHub Copilot prompts
# Reference the prompts in .github/prompts/
```

### Testing an Agent

```bash
# CLI mode
poetry run python {agent_name}/{agent_name}_agent.py

# Streamlit UI
streamlit run {agent_name}/{agent_name}_app.py

# Or use the convenience script
./{agent_name}/run_app.sh

# Run tests
make test-{agent_name}
```

## Testing

### Running Tests

```bash
# All tests
poetry run pytest .

# Specific agent
poetry run pytest {agent_name}/tests

# With coverage
poetry run pytest --cov={agent_name} {agent_name}/tests

# Core framework tests
make test-core
make test-core-coverage
```

### Test Structure

Each agent project includes:

- Unit tests for tools
- Integration tests for agent
- Streamlit app tests (optional)

## Environment Configuration

### Required Environment Variables

```bash
# Azure OpenAI
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_BASE_URL=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002
AZURE_OPENAI_EMBEDDING_ENDPOINT=https://your-resource.openai.azure.com/

# Environment
ENVIRONMENT=local  # local, demo, or sandbox
```

### Optional Environment Variables

```bash
# Azure Cosmos DB (if using CosmosDB persistence)
COSMOS_ENDPOINT=https://your-cosmos.documents.azure.com:443/
COSMOS_KEY=your_cosmos_key
COSMOS_DATABASE_NAME=chatbot
COSMOS_CONTAINER_NAME=conversations

# Application Insights (for telemetry)
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...
```

## Examples

The repository includes example implementations in [core/examples/](core/examples/):

### Math Agent (Semantic Kernel)

```bash
poetry run python core/examples/math_semantic_kernel_agent.py
```

### Math Agent (LlamaIndex)

```bash
poetry run python core/examples/math_llama_index_agent.py
```

### Math Streamlit App

```bash
streamlit run core/examples/math_app.py
```

## Best Practices

### When Creating Agents

1. **Start with clear requirements** - Define what the agent should do and who it's for
2. **Choose the right framework**:
   - Semantic Kernel for API integrations and general-purpose agents
   - LlamaIndex for document retrieval and data-heavy tasks
3. **Keep prompts focused** - One clear role per agent
4. **Add tools incrementally** - One at a time, fully tested before adding the next

### When Writing Tools

1. **Always return strings** - LLMs work best with text responses
2. **Validate all inputs** - Check for missing, empty, or invalid data
3. **Handle errors gracefully** - Return error messages, don't raise exceptions
4. **Use environment variables** - Never hardcode API keys or secrets
5. **Set timeouts** - Prevent hanging on slow API calls (10 seconds recommended)
6. **Document thoroughly** - Clear docstrings help both humans and LLMs

### When Customizing Prompts

1. Be specific about tool usage patterns
2. Provide examples of good interactions
3. Set clear boundaries (what NOT to do)
4. Update prompts whenever you add new tools
5. Keep prompts concise but comprehensive

### Security Best Practices

1. **Never commit secrets** - Use `.env` files (add to `.gitignore`)
2. **Validate all inputs** - Prevent injection attacks
3. **Use managed identities** - In Azure environments (production)
4. **Implement rate limiting** - For production deployments
5. **Sanitize tool outputs** - Before returning to users

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch** - `git checkout -b feature/my-feature`
3. **Follow code standards** - Run `make lint-all`
4. **Write tests** - Ensure coverage for new features
5. **Update documentation** - Keep README and prompts up to date
6. **Submit a pull request**

### Code Standards

- Python 3.10+ with type hints
- Black for code formatting (line length: 120)
- Ruff for linting
- mypy for type checking
- Google-style docstrings

## Support

For issues, questions, or contributions:

- **Issues**: Open an issue in this repository
- **Discussions**: Use GitHub Discussions

## Acknowledgments

- **Semantic Kernel** - [https://learn.microsoft.com/semantic-kernel/](https://learn.microsoft.com/semantic-kernel/)
- **LlamaIndex** - [https://docs.llamaindex.ai/](https://docs.llamaindex.ai/)
- **OpenTelemetry** - [https://opentelemetry.io/](https://opentelemetry.io/)
- **Streamlit** - [https://streamlit.io/](https://streamlit.io/)

---

**Ready to build your first agent?** Run `./core/scaffolding/create_agent_project.sh` to get started!
