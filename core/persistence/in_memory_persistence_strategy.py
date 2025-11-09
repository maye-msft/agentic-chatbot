"""Module for in-memory persistence strategy."""

import logging
from datetime import datetime
from typing import Any, Optional

from core.common import Message
from core.persistence import Conversation, PersistenceStrategy

logger = logging.getLogger("agentic_chatbot")


class InMemoryPersistenceStrategy(PersistenceStrategy):
    """
    An in-memory implementation of PersistenceStrategy for testing purposes.
    With multi-user support.
    """

    def __init__(self) -> None:
        # Store is now indexed by [user_id][conversation_id] to enforce user isolation
        self._store: dict[str, dict[str, dict[str, Any]]] = {}
        logger.info("Initialized InMemoryPersistenceStrategy with multi-user support.")

    async def save_conversation(self, conversation: Conversation, user_id: str) -> bool:
        """
        Save a conversation to in-memory store for a specific user.

        Args:
            conversation (Conversation): The conversation to save
            user_id (str): The ID of the user who owns this conversation

        Returns:
            bool: True if save was successful, False otherwise

        """
        # Initialize user dictionary if it doesn't exist
        if user_id not in self._store:
            self._store[user_id] = {}

        # Store the conversation data
        self._store[user_id][conversation.conversation_id] = {
            "conversation_id": conversation.conversation_id,
            "user_id": user_id,  # Add user_id field for consistency with CosmosDB implementation
            "agent_id": conversation.agent.id,
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "last_updated_at": conversation.last_updated_at.isoformat(),
            "messages": [
                {
                    "message_id": msg.message_id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                    "citations": [
                        {
                            "item_id": cit.item_id,
                            "source": cit.source,
                            "metadata": cit.metadata,
                        }
                        for cit in msg.citations
                    ],
                    "metadata": msg.metadata,
                }
                for msg in conversation.messages
            ],
            "metadata": conversation.metadata,
        }

        logger.info(f"Conversation '{conversation.conversation_id}' for user '{user_id}' saved to in-memory store.")
        return True

    async def load_conversation(self, conversation_id: str, user_id: str) -> Optional[dict[str, Any]]:
        """
        Load a conversation from in-memory store for a specific user.

        Args:
            conversation_id (str): The ID of the conversation to load
            user_id (str): The ID of the user who owns this conversation

        Returns:
            Optional[dict[str, Any]]: The conversation data if found, None otherwise

        """
        # Check if user exists in store
        if user_id not in self._store:
            logger.warning(
                f"User '{user_id}' not found in in-memory store when loading conversation '{conversation_id}'."
            )
            return None

        # Get conversation for this user
        conversation = self._store[user_id].get(conversation_id)

        if conversation:
            logger.info(f"Conversation '{conversation_id}' for user '{user_id}' loaded from in-memory store.")
        else:
            logger.warning(f"Conversation '{conversation_id}' for user '{user_id}' not found in in-memory store.")

        return conversation

    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Delete a conversation from in-memory store for a specific user.

        Args:
            conversation_id (str): The ID of the conversation to delete
            user_id (str): The ID of the user who owns this conversation

        Returns:
            bool: True if deletion was successful, False otherwise

        """
        # Check if user exists in store
        if user_id not in self._store:
            logger.warning(
                f"User '{user_id}' not found in in-memory store when deleting conversation '{conversation_id}'."
            )
            return False

        # Check if conversation exists for this user
        if conversation_id in self._store[user_id]:
            del self._store[user_id][conversation_id]
            logger.info(f"Conversation '{conversation_id}' for user '{user_id}' deleted from in-memory store.")
            return True

        logger.warning(
            f"Attempted to delete non-existent conversation '{conversation_id}' "
            f"for user '{user_id}' from in-memory store."
        )
        return False

    async def list_conversations(
        self,
        user_id: str,
        filters: Optional[dict[str, Any]] = None,
        page_size: int = 50,
        continuation_token: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        List conversation data from in-memory store with optional filtering and pagination.

        Args:
            user_id (str): The ID of the user whose conversations to list
            filters (Optional[dict[str, Any]]): Optional dictionary of filter conditions
            page_size (int): Number of items to return per page. Defaults to 50.
            continuation_token (Optional[str]): Index-based token for pagination (format: "index:N")

        Returns:
            dict[str, Any]: Dictionary containing:
                - items: List of dictionaries containing conversation metadata
                - continuation_token: Token for fetching the next page (None if no more pages)
                - total_count: Total count of matching items

        """
        # Initialize empty result if user not found
        if user_id not in self._store:
            logger.warning(f"User '{user_id}' not found in in-memory store when listing conversations.")
            return {"items": [], "continuation_token": None, "total_count": 0}

        # Get all conversations for this user
        user_conversations = list(self._store[user_id].values())

        # Initialize filters if None
        if filters is None:
            filters = {}

        # Apply additional filters (simple exact matching)
        filtered_conversations = [
            conv for conv in user_conversations if all(conv.get(k) == v for k, v in filters.items())
        ]

        # Get total count before pagination
        total_count = len(filtered_conversations)

        # Sort conversations by last_updated_at for consistent pagination
        sorted_conversations = sorted(
            # Most recent first
            filtered_conversations,
            key=lambda x: x.get("last_updated_at", ""),
            reverse=True,
        )

        # Get the starting index from continuation token
        start_index = 0
        if continuation_token and continuation_token.startswith("index:"):
            try:
                start_index = int(continuation_token.split(":", 1)[1])
            except (ValueError, IndexError):
                start_index = 0

        # Apply pagination
        end_index = min(start_index + page_size, len(sorted_conversations))
        page_items = sorted_conversations[start_index:end_index]

        # Create new continuation token if there are more items
        new_continuation_token = None
        if end_index < len(sorted_conversations):
            new_continuation_token = f"index:{end_index}"

        result = {"items": page_items, "continuation_token": new_continuation_token, "total_count": total_count}

        logger.info(
            f"Listing conversations for user '{user_id}' with filters {filters}: "
            f"Returning {len(page_items)} of {total_count} conversations "
            f"(page size: {page_size}, start index: {start_index})."
        )

        return result

    async def list_conversations_by_agent(
        self, user_id: str, agent_id: str, page_size: int = 50, continuation_token: Optional[str] = None
    ) -> dict[str, Any]:
        """
        List all conversations for a specific agent and user with pagination.

        Args:
            user_id (str): The ID of the user
            agent_id (str): The ID of the agent
            page_size (int): Number of items to return per page. Defaults to 50.
            continuation_token (Optional[str]): Token for continuation of a previous query

        Returns:
            dict[str, Any]: Dictionary containing:
                - items: List of conversation metadata
                - continuation_token: Token for fetching the next page (None if no more pages)
                - total_count: Total count of matching items

        """
        return await self.list_conversations(
            user_id=user_id, filters={"agent_id": agent_id}, page_size=page_size, continuation_token=continuation_token
        )

    async def reset_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Reset a conversation by removing all messages but keeping the conversation metadata.

        Args:
            conversation_id (str): The ID of the conversation to reset
            user_id (str): The ID of the user who owns this conversation

        Returns:
            bool: True if reset was successful, False otherwise

        """
        if user_id in self._store and conversation_id in self._store[user_id]:
            # Get the conversation dictionary
            conversation = self._store[user_id][conversation_id]

            # Create a new dictionary with empty messages
            self._store[user_id][conversation_id] = {
                "conversation_id": conversation["conversation_id"],
                "user_id": user_id,
                "agent_id": conversation["agent_id"],
                "title": conversation["title"],
                "created_at": conversation["created_at"],
                "last_updated_at": datetime.now().isoformat(),
                "messages": [],  # Clear all messages
                "metadata": conversation["metadata"],
            }

            logger.info(f"Reset conversation '{conversation_id}' for user '{user_id}' in memory.")
            return True

        logger.warning(f"Conversation '{conversation_id}' for user '{user_id}' not found in memory for reset.")
        return False

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
        try:
            # Check if user exists in store
            if user_id not in self._store:
                logger.warning(f"User '{user_id}' not found in store when appending message")
                return False

            # Check if conversation exists
            if conversation_id not in self._store[user_id]:
                logger.warning(
                    f"Conversation '{conversation_id}' not found for user '{user_id}' when appending message"
                )
                return False

            # Get the conversation
            conversation = self._store[user_id][conversation_id]

            # Serialize the message using its model_dump() method if available (Pydantic v2)
            # or dict() method (Pydantic v1)
            if hasattr(message, "model_dump"):
                # Pydantic v2
                message_dict = message.model_dump()
            else:
                # Pydantic v1 or manual serialization
                message_dict = {
                    "message_id": message.message_id,
                    "role": message.role,
                    "content": message.content,
                    "created_at": (
                        message.created_at.isoformat()
                        if isinstance(message.created_at, datetime)
                        else message.created_at
                    ),
                    "citations": [
                        {
                            "item_id": cit.item_id,
                            "source": cit.source,
                            "metadata": cit.metadata,
                        }
                        for cit in message.citations
                    ],
                    "metadata": message.metadata,
                    "attachments": message.attachments,
                }

            # Add the message to the conversation
            if "messages" not in conversation:
                conversation["messages"] = []

            conversation["messages"].append(message_dict)

            # Update last_updated_at
            conversation["last_updated_at"] = datetime.now().isoformat()

            logger.info(f"Message appended to conversation '{conversation_id}' for user '{user_id}' in memory")
            return True

        except Exception as e:
            logger.error(f"Error appending message to conversation '{conversation_id}': {str(e)}")
            return False
