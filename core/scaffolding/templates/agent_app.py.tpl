"""
Streamlit app for {{AGENT_NAME}}.

This app demonstrates how to instantiate the StreamlitConversationApp class with:
- JSON file persistence strategy for storing conversations
- {{AGENT_NAME}}

To run this app:
    streamlit run {{PROJECT_NAME}}/{{PROJECT_NAME}}_app.py
"""

from {{PROJECT_NAME}}.{{PROJECT_NAME}}_agent import {{AGENT_CLASS_NAME}}
from core.persistence.json_file_persistence_strategy import JsonFilePersistenceStrategy
from core.streamlit_app import StreamlitConversationApp


def create_{{PROJECT_NAME}}_app() -> StreamlitConversationApp:
    """
    Create and return a StreamlitConversationApp instance with JSON file storage
    and {{AGENT_NAME}}.

    This function demonstrates how to:
    1. Initialize a custom persistence strategy (JSON file storage)
    2. Define available agents
    3. Create the app with these configurations

    Returns:
        StreamlitConversationApp: Configured app instance ready to run.

    Example:
        >>> app = create_{{PROJECT_NAME}}_app()
        >>> app.run()

    """
    # Define the persistence strategy: JSON file storage
    persistence_strategy = JsonFilePersistenceStrategy()

    # Define available agents
    agents = {
        "{{AGENT_ID}}": {{AGENT_CLASS_NAME}}(),
    }

    # Create and return the app with the specified configuration
    return StreamlitConversationApp(
        persistence_strategy=persistence_strategy,
        agents=agents,
        title="{{AGENT_NAME}}",
    )


if __name__ == "__main__":
    # Create the app with JSON storage and agents
    app = create_{{PROJECT_NAME}}_app()

    # Run the Streamlit app
    app.run()
