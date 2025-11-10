"""{{AGENT_NAME}} implementation."""

import logging
import uuid
from datetime import datetime
from pathlib import Path

from core.agents.semantic_kernel_agent import AbstractSemanticKernelAgent
from core.persistence import Conversation
from core.persistence.json_file_persistence_strategy import JsonFilePersistenceStrategy
from core.tools import AbstractTool
from core.trace.otel_configurator import OtelConfigurator

# Configure logging
OtelConfigurator.configure()
logger = logging.getLogger("agentic_chatbot")


class {{AGENT_CLASS_NAME}}(AbstractSemanticKernelAgent):
    """{{AGENT_NAME}} implementation."""

    def __init__(self) -> None:
        # Load prompt from file
        prompt_file = Path(__file__).parent / "{{PROJECT_NAME}}_prompt.txt"
        with open(prompt_file, "r") as f:
            prompt = f.read()

        super().__init__(
            agent_id="{{AGENT_ID}}",
            name="{{AGENT_NAME}}",
            description="{{AGENT_DESCRIPTION}}",
            prompt=prompt,
            tools={
{{TOOL_DICT}}
            },
        )
        self.persistence_strategy = JsonFilePersistenceStrategy(base_dir="./.tmp")


async def main() -> None:
    """
    Demonstrate usage of {{AGENT_CLASS_NAME}}.

    Includes processing a sample question and persisting the conversation.
    """
    user_id = "user123"
    question = "Sample question for {{AGENT_NAME}}"
    agent = {{AGENT_CLASS_NAME}}()
    response = await agent.process(question)

    # Create agent message dict for local state
    agent_message_dict = {
        "message_id": response.message_id,
        "role": response.role,
        "content": response.content,
        "created_at": (
            response.created_at.isoformat()
            if hasattr(response.created_at, "isoformat")
            else response.created_at
        ),
        "citations": (
            [
                {"item_id": cit.item_id, "source": cit.source, "metadata": cit.metadata}
                for cit in response.citations
            ]
            if hasattr(response, "citations") and response.citations
            else []
        ),
        "metadata": response.metadata if hasattr(response, "metadata") else {},
        "attachments": [],
    }
    logger.info(f"Agent message: {agent_message_dict}")

    # Demonstrate persistence usage
    persistence = agent.persistence_strategy

    # Create a conversation object
    conversation_id = str(uuid.uuid4())
    conversation = Conversation(
        conversation_id=conversation_id,
        agent=agent,
        title="{{AGENT_NAME}} Conversation",
        created_at=datetime.now(),
        last_updated_at=datetime.now(),
        messages=[response],
        metadata={},
    )

    # Save the conversation
    await persistence.save_conversation(conversation, user_id)
    logger.info(f"Conversation {conversation_id} saved.")

    # Load the conversation
    loaded = await persistence.load_conversation(conversation_id, user_id)
    logger.info(f"Loaded conversation: {loaded}")

    # List conversations for the user
    listed = await persistence.list_conversations(user_id)
    logger.info(f"List of conversations for user: {listed}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
