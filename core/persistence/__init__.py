from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, ClassVar, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from core.agents.abstract_agent import Agent
from core.common import Message


class Conversation(BaseModel):
    """
    Represents an entire conversation with multiple messages.

    Attributes:
        conversation_id (str): Unique identifier for the conversation
        agent (Agent): The agent used in the conversation
        title (str): User-friendly title for the conversation
        created_at (datetime): Timestamp when the conversation was created
        last_updated_at (datetime): Timestamp when the conversation was last modified
        messages (list[Message]): List of all messages in the conversation
        metadata (dict[str, Any]): Additional information about the conversation
        model_config (ClassVar[ConfigDict]): Pydantic model configuration options

    """

    conversation_id: str
    agent: Agent
    title: str
    created_at: datetime
    last_updated_at: datetime
    messages: list[Message]
    metadata: dict[str, Any]

    model_config: ClassVar[ConfigDict] = {"arbitrary_types_allowed": True}

    @field_validator("agent", mode="before")
    @classmethod
    def validate_agent(cls, v: Any) -> Any:
        """
        Validate that the agent has the required Agent interface methods and properties.
        This allows for more flexible validation of agent instances.
        """
        # If it's already an Agent instance, allow it
        if isinstance(v, Agent):
            return v

        # Check if it has the required Agent interface
        required_properties = {"id", "name", "description", "prompt", "tools", "settings"}
        required_methods = {"initialize", "process", "add_tool", "to_dict", "reset_conversation", "update_chat_history"}

        has_properties = all(hasattr(v, prop) for prop in required_properties)
        has_methods = all(callable(getattr(v, method, None)) for method in required_methods)

        if has_properties and has_methods:
            return v

        raise ValueError(f"Agent must implement the Agent interface. Got {type(v)}")


class PersistenceStrategy(ABC):
    """
    Interface for persistence operations.
    Defines how conversation data is stored and retrieved.
    """

    @abstractmethod
    async def save_conversation(self, conversation: "Conversation", user_id: str) -> bool:
        """
        Save a conversation to persistent storage.

        Args:
            conversation (Conversation): The conversation to save
            user_id (str): The ID of the user who owns this conversation

        Returns:
            bool: True if save was successful, False otherwise

        """
        pass

    @abstractmethod
    async def load_conversation(self, conversation_id: str, user_id: str) -> Optional[dict[str, Any]]:
        """
        Load a conversation data from persistent storage.

        Args:
            conversation_id (str): The ID of the conversation to load
            user_id (str): The ID of the user who owns this conversation

        Returns:
            Optional[dict[str, Any]]: The conversation data if found, None otherwise

        """
        pass

    @abstractmethod
    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Delete a conversation from persistent storage.

        Args:
            conversation_id (str): The ID of the conversation to delete
            user_id (str): The ID of the user who owns this conversation

        Returns:
            bool: True if deletion was successful, False otherwise

        """
        pass

    @abstractmethod
    async def list_conversations(
        self,
        user_id: str,
        filters: Optional[dict[str, Any]] = None,
        page_size: int = 50,
        continuation_token: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        List conversation data from persistent storage with optional filtering and pagination.

        Args:
            user_id (str): The ID of the user whose conversations to list
            filters (Optional[dict[str, Any]]): Optional dictionary of filter conditions
            page_size (int): Number of items to return per page (default: 50)
            continuation_token (Optional[str]): Token for continuation of a previous query

        Returns:
            dict[str, Any]: Dictionary containing:
                - items: List of dictionaries containing conversation metadata including agent_ids
                - continuation_token: Token for fetching the next page (None if no more pages)
                - total_count: Total count of matching items

        """
        pass

    @abstractmethod
    async def reset_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Reset a conversation by removing all messages but keeping the conversation metadata.

        Args:
            conversation_id (str): The ID of the conversation to reset
            user_id (str): The ID of the user who owns this conversation

        Returns:
            bool: True if reset was successful, False otherwise

        """
        pass

    @abstractmethod
    async def append_message(self, conversation_id: str, user_id: str, message: Message) -> bool:
        """
        Append a single message to an existing conversation without rewriting all messages.
        This is a more efficient way to add new messages compared to saving the entire conversation.

        Args:
            conversation_id (str): The ID of the conversation to append the message to
            user_id (str): The ID of the user who owns this conversation
            message (Message): The Message object to append

        Returns:
            bool: True if append was successful, False otherwise

        """
        pass
