"""
Example Streamlit app using math agents from the examples folder.

This app demonstrates how to instantiate the StreamlitConversationApp class with:
- JSON file persistence strategy for storing conversations
- Available math agents from the examples folder (Math LlamaIndex and Math Semantic Kernel)

To run this app:
    streamlit run core/examples/math_app.py
"""

from core.examples.math_llama_index_agent import MathLlamaIndexAgent
from core.examples.math_semantic_kernel_agent import MathSemanticKernelAgent
from core.persistence.json_file_persistence_strategy import JsonFilePersistenceStrategy
from core.streamlit_app import StreamlitConversationApp


def create_math_app() -> StreamlitConversationApp:
    """
    Create and return a StreamlitConversationApp instance with JSON file storage
    and the example math agents.

    This function demonstrates how to:
    1. Initialize a custom persistence strategy (JSON file storage)
    2. Define available math agents from the examples folder
    3. Create the app with these configurations

    Returns:
        StreamlitConversationApp: Configured app instance ready to run.

    Example:
        >>> app = create_math_app()
        >>> app.run()

    """
    # Define the persistence strategy: JSON file storage
    persistence_strategy = JsonFilePersistenceStrategy()

    # Define available math agents from the examples folder
    agents = {
        "math_llama_index_agent": MathLlamaIndexAgent(),
        "math_semantic_kernel_agent": MathSemanticKernelAgent(),
    }

    # Create and return the app with the specified configuration
    return StreamlitConversationApp(
        persistence_strategy=persistence_strategy,
        agents=agents,
        title="Math Agents Demo",
    )


if __name__ == "__main__":
    # Create the app with JSON storage and example math agents
    app = create_math_app()

    # Run the Streamlit app
    app.run()
