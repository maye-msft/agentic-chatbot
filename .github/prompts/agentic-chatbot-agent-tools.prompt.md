---
mode: 'agent'
description: 'Step 3: Add one tool to the agent'
---

# Add Agent Tool

Add **ONE tool** to the agent with complete, production-ready implementation.

**Note**: This prompt adds one tool at a time. Repeat to add more tools.

## Instructions

1. **Collect information for ONE tool:**
   - Project name (e.g., `weather_agent`, `stock_agent`)
   - Tool name (e.g., `get_weather`, `get_stock_price`)
   - What the tool does
   - Parameters and types
   - Return type
   - Data source (API, database, calculation, etc.)
   - API keys/credentials needed
   - Dependencies required

2. **Read existing tools file:**
   ```bash
   cat {project}/{project}_tools.py
   ```
   Check if there are existing tools to preserve.

3. **Add the new tool function:**

   Append to `{project}/{project}_tools.py`:
   ```python
   def tool_name(param: type) -> str:
       """
       Brief description.

       Args:
           param (type): Description

       Returns:
           str: Description
       """
       # Validate inputs
       if not param:
           return "Error: param is required"

       # Get API key if needed
       api_key = os.getenv("API_KEY_NAME")
       if not api_key:
           return "Error: API_KEY_NAME not set. Get it from https://..."

       try:
           # Implementation
           result = do_something(param)
           return result
       except SpecificException as e:
           return f"Error: {str(e)}"
       except Exception as e:
           return f"Unexpected error: {str(e)}"
   ```

   **Important**:
   - Add necessary imports at the top
   - Preserve all existing tools
   - Only add the NEW tool function

4. **Add dependencies if needed:**
   ```bash
   poetry add {package} --group {project}
   ```

5. **Update agent file to register the tool:**

   Add import and tool registration:
   ```python
   # Add to imports (if new tool)
   from {project}.{project}_tools import ..., new_tool

   # In __init__, add to tools dict:
   tools={
       # ... existing tools ...
       "New Tool": AbstractTool(
           name="New Tool",
           description="Description",
           function=new_tool
       ),
   }
   ```

6. **Update prompt file:**

   Add the tool to "Your Capabilities" section in `{project}/{project}_prompt.txt`:
   ```
   ## Your Capabilities
   You have access to the following tools:
   - existing_tool: Description
   - new_tool: Description of the new tool
   ```

7. **Inform user:**
   ```
   ✅ Tool added: {tool_name}

   📝 Files updated:
     - {project}/{project}_tools.py (added {tool_name})
     - {project}/{project}_agent.py (registered {tool_name})
     - {project}/{project}_prompt.txt (listed {tool_name})

   📦 Dependencies added: {list if any}

   🔑 Environment variables: {list if any}

   🚀 Test:
     poetry run python {project}/{project}_agent.py

   💡 Repeat this prompt to add more tools!
   ```

## Example

**User**: "Add get_stock_price tool to stock_agent using yfinance"

**Read existing file**:
```bash
cat stock_agent/stock_agent_tools.py
# Shows: """Tools for Stock Agent."""
```

**Add new tool function** to [stock_agent/stock_agent_tools.py](stock_agent/stock_agent_tools.py):
```python
"""Tools for Stock Agent."""

import yfinance as yf


def get_stock_price(ticker: str) -> str:
    """
    Get current stock price for a ticker symbol.

    Args:
        ticker (str): Stock ticker symbol (e.g., "AAPL", "GOOGL")

    Returns:
        str: Current price information or error message
    """
    if not ticker or not ticker.strip():
        return "Error: Ticker symbol is required"

    ticker = ticker.strip().upper()

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or 'currentPrice' not in info:
            return f"Error: Could not find data for ticker '{ticker}'"

        price = info.get('currentPrice', 'N/A')
        prev_close = info.get('previousClose', 'N/A')
        change = info.get('regularMarketChangePercent', 0)

        return f"""Stock: {ticker}
💰 Current Price: ${price}
📊 Previous Close: ${prev_close}
📈 Change: {change:+.2f}%"""

    except Exception as e:
        return f"Error fetching stock data: {str(e)}"
```

**Update agent file** [stock_agent/stock_agent_agent.py](stock_agent/stock_agent_agent.py):
```python
# Add import
from stock_agent.stock_agent_tools import get_stock_price

# In __init__, add to tools:
tools={
    "Get Stock Price": AbstractTool(
        name="Get Stock Price",
        description="Get current stock price for a ticker symbol",
        function=get_stock_price
    ),
}
```

**Update prompt file** [stock_agent/stock_agent_prompt.txt](stock_agent/stock_agent_prompt.txt):
```
## Your Capabilities
You have access to the following tools:
- get_stock_price: Get current stock price and price changes for any ticker symbol
```

**Add dependency**:
```bash
poetry add yfinance --group stock_agent
```

**Result**:
```
✅ Tool added: get_stock_price

📝 Files updated:
  - stock_agent/stock_agent_tools.py (added get_stock_price)
  - stock_agent/stock_agent_agent.py (registered get_stock_price)
  - stock_agent/stock_agent_prompt.txt (listed get_stock_price)

📦 Dependencies added: yfinance

🚀 Test:
  poetry run python stock_agent/stock_agent_agent.py

💡 Repeat this prompt to add more tools!
```

## Notes

- **ONE tool per invocation** - keeps changes focused
- Preserves existing tools in the file
- Always return strings (LLM-friendly)
- Include comprehensive error handling
- Validate all inputs
- Use environment variables for secrets
- Include timeouts for API calls (10 seconds recommended)
- Never hardcode API keys
