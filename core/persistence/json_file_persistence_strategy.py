"""Persistence strategy for saving conversation history as JSON files in /tmp."""

import glob
import json
import logging
import os
from datetime import datetime
from typing import Any, Optional

from core.common import Message
from core.persistence import Conversation, PersistenceStrategy

logger = logging.getLogger("agentic_chatbot")

TMP_DIR = "../../.tmp"


class JsonFilePersistenceStrategy(PersistenceStrategy):
    """
    Persistence strategy that saves each conversation as a JSON file in /tmp.

    File name format: {user_id}_{conversation_id}.json.

    Args:
        base_dir (str): Directory where conversation files are stored.

    """

    def __init__(self, base_dir: str = TMP_DIR) -> None:
        cuurrent_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.join(cuurrent_dir, base_dir)
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        logger.info(f"Initialized JsonFilePersistenceStrategy with base_dir={self.base_dir}")

    def _get_filepath(self, conversation_id: str, user_id: str) -> str:
        return os.path.join(self.base_dir, f"{user_id}_{conversation_id}.json")

    async def _serialize_for_json(self, obj: Any) -> Any:
        """
        Ensure all objects are fully serializable for CosmosDB.
        This is a deep serialization function that handles nested structures.

        Args:
            obj (Any): Any Python object to be serialized

        Returns:
            Any: A fully serializable version of the object

        """
        try:
            # Test if object is directly JSON serializable
            json.dumps(obj)
            return obj
        except (TypeError, OverflowError, ValueError):
            # If it's not directly serializable, we need to convert it
            pass

        # Handle different types
        if isinstance(obj, dict):
            # Process each key-value pair in dictionaries
            return {k: await self._serialize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            # Process each item in lists
            return [await self._serialize_for_json(item) for item in obj]
        elif isinstance(obj, tuple):
            # Convert tuples to lists
            return [await self._serialize_for_json(item) for item in obj]
        elif hasattr(obj, "__dict__"):
            # For class instances, convert to dict of attributes
            return await self._serialize_for_json(obj.__dict__)
        elif hasattr(obj, "isoformat"):
            # Handle datetime objects
            return obj.isoformat()
        else:
            # For any other type, convert to string
            return str(obj)

    async def _serialize_message(self, msg: dict[str, Any]) -> dict[str, Any]:
        """
        Serialize a message to a dictionary format ensuring all nested objects are serializable.

        Args:
            msg (dict[str, Any]): The message object to serialize

        Returns:
            dict[str, Any]: The serialized message

        """
        serialized_msg = {
            "message_id": msg.get("message_id"),
            "role": msg.get("role"),
            "content": msg.get("content", ""),
            "created_at": (
                msg["created_at"].isoformat() if isinstance(msg["created_at"], datetime) else str(msg["created_at"])
            ),
        }

        # Serialize metadata
        try:
            serialized_msg["metadata"] = await self._serialize_for_json(msg.get("metadata", {}))
        except Exception as e:
            logger.error(f"Error serializing metadata for message {msg.get('message_id', 'unknown')}: {str(e)}")
            serialized_msg["metadata"] = {"error": f"Failed to serialize metadata: {str(e)}"}

        # Serialize citations
        try:
            serialized_msg["citations"] = await self._serialize_for_json(msg.get("citations", []))
        except Exception as e:
            logger.error(f"Error serializing citations for message {msg.get('message_id', 'unknown')}: {str(e)}")
            serialized_msg["citations"] = [{"error": f"Failed to serialize citations: {str(e)}"}]

        # Serialize attachments
        try:
            serialized_msg["attachments"] = await self._serialize_for_json(msg.get("attachments", []))
        except Exception as e:
            logger.error(f"Error serializing attachments for message {msg.get('message_id', 'unknown')}: {str(e)}")
            serialized_msg["attachments"] = [{"error": f"Failed to serialize attachments: {str(e)}"}]

        print(f"Serialized message: {serialized_msg}")
        return serialized_msg

    async def save_conversation(self, conversation: Conversation, user_id: str) -> bool:
        """
        Save a conversation to a JSON file.

        Args:
            conversation (Conversation): The Conversation object to save.
            user_id (str): The user ID associated with the conversation.

        Returns:
            bool: True if saved successfully, False otherwise.

        """
        try:
            filepath = self._get_filepath(conversation.conversation_id, user_id)
            # Serialize conversation to dict
            data = {
                "conversation_id": conversation.conversation_id,
                "user_id": user_id,
                "agent_id": conversation.agent.id,
                "title": conversation.title,
                "created_at": conversation.created_at.isoformat(),
                "last_updated_at": conversation.last_updated_at.isoformat(),
                "messages": [
                    await self._serialize_message(
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
                            "attachments": getattr(msg, "attachments", []),
                        }
                    )
                    for msg in conversation.messages
                ],
                "metadata": conversation.metadata,
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved conversation '{conversation.conversation_id}' for user '{user_id}' to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            return False

    async def load_conversation(self, conversation_id: str, user_id: str) -> Optional[dict[str, Any]]:
        """
        Load a conversation from a JSON file.

        Args:
            conversation_id (str): The conversation ID.
            user_id (str): The user ID associated with the conversation.

        Returns:
            Optional[dict[str, Any]]: The conversation data as a dict, or None if not found or error.

        """
        filepath = self._get_filepath(conversation_id, user_id)
        if not os.path.exists(filepath):
            logger.warning(f"Conversation file not found: {filepath}")
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"Loaded conversation '{conversation_id}' for user '{user_id}' from {filepath}")
            return data
        except Exception as e:
            logger.error(f"Failed to load conversation: {e}")
            return None

    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Delete a conversation JSON file.

        Args:
            conversation_id (str): The conversation ID.
            user_id (str): The user ID associated with the conversation.

        Returns:
            bool: True if deleted successfully, False otherwise.

        """
        filepath = self._get_filepath(conversation_id, user_id)
        if not os.path.exists(filepath):
            logger.warning(f"Conversation file not found for delete: {filepath}")
            return False
        try:
            os.remove(filepath)
            logger.info(f"Deleted conversation '{conversation_id}' for user '{user_id}' from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete conversation: {e}")
            return False

    async def list_conversations(
        self,
        user_id: str,
        filters: Optional[dict[str, Any]] = None,
        page_size: int = 50,
        continuation_token: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        List conversation metadata for a user, with optional filters and pagination.

        Args:
            user_id (str): The user ID.
            filters (Optional[dict[str, Any]]): Optional dict of filters to apply.
            page_size (int): Number of items per page. Default is 50.
            continuation_token (Optional[str]): Token for pagination.

        Returns:
            dict[str, Any]: Dict with items, continuation_token, and total_count.

        """
        pattern = os.path.join(self.base_dir, f"{user_id}_*.json")
        files = sorted(glob.glob(pattern), reverse=True)
        # Pagination
        start_index = 0
        if continuation_token and continuation_token.startswith("index:"):
            try:
                start_index = int(continuation_token.split(":", 1)[1])
            except Exception:
                start_index = 0
        end_index = min(start_index + page_size, len(files))
        page_files = files[start_index:end_index]
        items = []
        for fp in page_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Apply filters (exact match)
                if filters:
                    if not all(data.get(k) == v for k, v in filters.items()):
                        continue
                # Only include metadata (no messages)
                item = {k: data[k] for k in data if k != "messages"}
                items.append(item)
            except Exception as e:
                logger.warning(f"Failed to read conversation file {fp}: {e}")
        new_continuation_token = None
        if end_index < len(files):
            new_continuation_token = f"index:{end_index}"
        return {
            "items": items,
            "continuation_token": new_continuation_token,
            "total_count": len(files),
        }

    async def reset_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Reset a conversation by clearing its messages.

        Args:
            conversation_id (str): The conversation ID.
            user_id (str): The user ID associated with the conversation.

        Returns:
            bool: True if reset successfully, False otherwise.

        """
        filepath = self._get_filepath(conversation_id, user_id)
        if not os.path.exists(filepath):
            logger.warning(f"Conversation file not found for reset: {filepath}")
            return False
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["messages"] = []
            data["last_updated_at"] = datetime.now().isoformat()
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Reset conversation '{conversation_id}' for user '{user_id}' in {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to reset conversation: {e}")
            return False

    async def append_message(self, conversation_id: str, user_id: str, message: Message) -> bool:
        """
        Append a message to a conversation JSON file.

        Args:
            conversation_id (str): The conversation ID.
            user_id (str): The user ID associated with the conversation.
            message (Message): The Message object to append.

        Returns:
            bool: True if appended successfully, False otherwise.

        """
        filepath = self._get_filepath(conversation_id, user_id)
        if not os.path.exists(filepath):
            logger.warning(f"Conversation file not found for append: {filepath}")
            return False
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Serialize message
            msg_dict = {
                "message_id": message.message_id,
                "role": message.role,
                "content": message.content,
                "created_at": (
                    message.created_at.isoformat() if isinstance(message.created_at, datetime) else message.created_at
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
                "attachments": getattr(message, "attachments", []),
            }
            serialized_msg_dict = await self._serialize_message(msg_dict)
            data.setdefault("messages", []).append(serialized_msg_dict)
            data["last_updated_at"] = datetime.now().isoformat()
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Appended message to conversation '{conversation_id}' for user '{user_id}' in {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to append message: {e}")
            return False
