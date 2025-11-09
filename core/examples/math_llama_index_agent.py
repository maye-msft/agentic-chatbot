"""Module defines a Math Llama Index Agent that can perform basic arithmetic operations."""

import logging
import uuid
from datetime import datetime

from core.agents.llama_index_agent import AbstractLlamaIndexAgent
from core.examples.math_tools import add, divide, multiply, subtract
from core.persistence import Conversation
from core.persistence.json_file_persistence_strategy import JsonFilePersistenceStrategy
from core.tools import AbstractTool
from core.trace.otel_configurator import OtelConfigurator

# Configure logging
OtelConfigurator.configure()
logger = logging.getLogger("agentic_chatbot")


class MathLlamaIndexAgent(AbstractLlamaIndexAgent):
    """A Llama Index Agent that can help you with math problems."""

    def __init__(self) -> None:
        super().__init__(
            agent_id="math_llama_index_agent",
            name="Math Llama Index Agent",
            description="A Llama Index Agent that can help you with math problems",
            prompt=(
                "You can solve math problems with the following tools: Add, Subtract, Multiply, Divide. "
                "Please use a tool to solve math problems before you solve the math problem by yourself."
            ),
            tools={
                "Add": AbstractTool(name="Add", description="Add two numbers, such as 6+3", function=add),
                "Subtract": AbstractTool(
                    name="Subtract", description="Subtract two numbers, such as 6-3", function=subtract
                ),
                "Multiply": AbstractTool(
                    name="Multiply", description="Multiply two numbers, such as 6*3", function=multiply
                ),
                "Divide": AbstractTool(name="Divide", description="Divide two numbers, such as 6/3", function=divide),
            },
        )
        self.persistence_strategy = JsonFilePersistenceStrategy(base_dir="./.tmp")


async def main() -> None:
    """
    Demonstrate usage of MathLlamaIndexAgent.

    Includes processing a math question and persisting the conversation.
    """
    user_id = "user123"
    question = "What is 6 + 3?"
    agent = MathLlamaIndexAgent()
    response = await agent.process(question)

    # Create agent message dict for local state
    agent_message_dict = {
        "message_id": response.message_id,
        "role": response.role,
        "content": response.content,
        "created_at": response.created_at if isinstance(response.created_at, str) else response.created_at.isoformat(),
        "citations": (
            [{"item_id": cit.item_id, "source": cit.source, "metadata": cit.metadata} for cit in response.citations]
            if hasattr(response, "citations") and response.citations
            else []
        ),
        "metadata": response.metadata if hasattr(response, "metadata") else {},
        "attachments": [],
    }
    logger.info(f"Agent message:{agent_message_dict}")

    # Demonstrate persistence usage
    persistence = agent.persistence_strategy

    # Create a conversation object
    conversation_id = str(uuid.uuid4())
    conversation = Conversation(
        conversation_id=conversation_id,
        agent=agent,
        title="Math Conversation",
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
    logger.info(f"Loaded conversation:{loaded}")

    # List conversations for the user
    listed = await persistence.list_conversations(user_id)
    logger.info(f"List of conversations for user:{listed}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
