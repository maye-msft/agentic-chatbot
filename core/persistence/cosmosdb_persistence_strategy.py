"""Module for cosmos persistence strategy."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Optional

from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from core.common import Message
from core.persistence import Conversation, PersistenceStrategy

load_dotenv()

# Configure logging
logger = logging.getLogger("agentic_chatbot")


# CosmosDB Persistence Strategy
class CosmosDBPersistenceStrategy(PersistenceStrategy):
    """
    An implementation of PersistenceStrategy using Azure CosmosDB with DefaultAzureCredential.

    Stores conversation metadata and messages in separate containers to work around the 2MB size limitation.

    Args:
        cosmos_endpoint (str): The Cosmos DB endpoint (e.g., https://example.documents.azure.com:443/)
        database_name (str): The name of the database to use
        conversation_container_name (str): The name of the container to store conversation metadata
        messages_container_name (str): The name of the container to store conversation messages
        partition_key (str): The partition key to use (default: "/user_id")

    Raises:
        ValueError: If any of the parameters are invalid or empty

    """

    def __init__(
        self,
        cosmos_endpoint: str,
        database_name: str,
        conversation_container_name: str,
        messages_container_name: str,
        partition_key: str = "/user_id",
    ):
        # Clean input parameters
        cosmos_endpoint = cosmos_endpoint.strip().rstrip("/")
        database_name = database_name.strip()
        conversation_container_name = conversation_container_name.strip()
        messages_container_name = messages_container_name.strip()

        # Validate parameters
        if not cosmos_endpoint:
            raise ValueError("CosmosDB endpoint cannot be empty")
        if not database_name:
            raise ValueError("Database name cannot be empty")
        if not conversation_container_name:
            raise ValueError("Conversation container name cannot be empty")
        if not messages_container_name:
            raise ValueError("Messages container name cannot be empty")

        # Validate endpoint format
        if not cosmos_endpoint.startswith("https://"):
            logger.warning(f"CosmosDB endpoint '{cosmos_endpoint}' doesn't start with 'https://'")

        logger.info(f"Initializing CosmosDB client for endpoint: {cosmos_endpoint}")

        # Use DefaultAzureCredential for authentication
        try:
            credential = DefaultAzureCredential()
            logger.info("Successfully created DefaultAzureCredential")
        except Exception as e:
            error_msg = f"Failed to create DefaultAzureCredential: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e

        try:
            self.client = CosmosClient(cosmos_endpoint, credential)
            logger.info("Successfully created CosmosClient")
        except Exception as e:
            error_msg = f"Failed to create CosmosClient: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e

        self.database_name = database_name
        self.conversation_container_name = conversation_container_name
        self.messages_container_name = messages_container_name
        self.partition_key = PartitionKey(path=partition_key)

        # Create database and containers if they don't exist
        self._ensure_database_and_containers()

        logger.info(
            "Initialized CosmosDBPersistenceStrategy with DefaultAzureCredential "
            f"for database '{database_name}', conversation container "
            f"'{conversation_container_name}', and messages container "
            f"'{messages_container_name}'."
        )

    def _ensure_database_and_containers(self) -> None:
        """
        Create database and containers if they don't exist.

        Raises:
            ValueError: If there is an error creating or connecting to the database or containers

        """
        # Create database if it doesn't exist
        try:
            logger.info(f"Attempting to create or connect to database '{self.database_name}'")
            self.database = self.client.create_database_if_not_exists(id=self.database_name)
            logger.info(f"Successfully connected to database '{self.database_name}'")
        except exceptions.CosmosHttpResponseError as e:
            error_msg = f"Failed to connect to or create database '{self.database_name}': {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e

        # Create conversation container if it doesn't exist
        try:
            logger.info(f"Attempting to create or connect to container '{self.conversation_container_name}'")
            self.conversation_container = self.database.create_container_if_not_exists(
                id=self.conversation_container_name, partition_key=self.partition_key
            )
            logger.info(f"Successfully connected to container '{self.conversation_container_name}'")
        except exceptions.CosmosHttpResponseError as e:
            error_msg = f"Failed to connect to or create container '{self.conversation_container_name}': {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e

        # Create messages container if it doesn't exist
        try:
            logger.info(f"Attempting to create or connect to container '{self.messages_container_name}'")
            # CRITICAL FIX: Use different container name for messages to ensure separation
            # Create messages container with conversation_id as partition key
            messages_partition_key = PartitionKey(path="/conversation_id")
            self.messages_container = self.database.create_container_if_not_exists(
                id=self.messages_container_name, partition_key=messages_partition_key
            )

            # Verify the containers are different
            if self.messages_container_name == self.conversation_container_name:
                error_msg = "Messages container and conversation container cannot have the same name"
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.info(f"Successfully connected to messages container '{self.messages_container_name}'")
        except exceptions.CosmosHttpResponseError as e:
            error_msg = f"Failed to connect to or create container '{self.messages_container_name}': {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e

    async def _serialize_for_cosmos(self, obj: Any) -> Any:
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
            return {k: await self._serialize_for_cosmos(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            # Process each item in lists
            return [await self._serialize_for_cosmos(item) for item in obj]
        elif isinstance(obj, tuple):
            # Convert tuples to lists
            return [await self._serialize_for_cosmos(item) for item in obj]
        elif hasattr(obj, "__dict__"):
            # For class instances, convert to dict of attributes
            return await self._serialize_for_cosmos(obj.__dict__)
        elif hasattr(obj, "isoformat"):
            # Handle datetime objects
            return obj.isoformat()
        else:
            # For any other type, convert to string
            return str(obj)

    async def _serialize_message(self, msg: Message) -> dict[str, Any]:
        """
        Serialize a message to a dictionary format ensuring all nested objects are serializable.

        Args:
            msg (Message): The message object to serialize

        Returns:
            dict[str, Any]: The serialized message

        """
        try:
            # First create basic dictionary with direct attributes
            basic_dict = {
                "message_id": msg.message_id,
                "role": msg.role,
                "content": msg.content,
                "created_at": convert_to_isoformat(msg.created_at),
                "citations": [],
                "attachments": [],
                "metadata": {},
            }

            # Safely add metadata if it exists
            if hasattr(msg, "metadata") and msg.metadata is not None:
                try:
                    # Ensure metadata is fully serializable
                    basic_dict["metadata"] = await self._serialize_for_cosmos(msg.metadata)
                except Exception as e:
                    logger.error(f"Error serializing metadata for message {msg.message_id}: {str(e)}")
                    basic_dict["metadata"] = {"error": f"Failed to serialize: {str(e)}"}

            # Handle citations
            if hasattr(msg, "citations") and msg.citations is not None:
                try:
                    # Use our deep serialization method to ensure all citation objects are serializable
                    basic_dict["citations"] = await self._serialize_for_cosmos(msg.citations)
                except Exception as e:
                    logger.error(f"Error serializing citations for message {msg.message_id}: {str(e)}")
                    basic_dict["citations"] = [{"error": f"Failed to serialize: {str(e)}"}]

            # Handle attachments
            if hasattr(msg, "attachments") and msg.attachments is not None:
                try:
                    # Use our deep serialization method for attachments too
                    basic_dict["attachments"] = await self._serialize_for_cosmos(msg.attachments)
                except Exception as e:
                    logger.error(f"Error serializing attachments for message {msg.message_id}: {str(e)}")
                    basic_dict["attachments"] = [{"error": f"Failed to serialize: {str(e)}"}]

            # Final safety check - ensure entire dictionary is serializable
            try:
                json.dumps(basic_dict)
                return basic_dict
            except (TypeError, OverflowError):
                # If still not serializable, return a simplified version
                logger.error(f"Message {msg.message_id} still not fully serializable after processing")
                return {
                    "message_id": msg.message_id,
                    "role": msg.role,
                    "content": "Error: Message content could not be serialized for storage",
                    "created_at": convert_to_isoformat(msg.created_at.isoformat()),
                    "error": "Serialization failure",
                    "citations": [],
                    "attachments": [],
                }
        except Exception as e:
            logger.error(f"Unexpected error in _serialize_message for {msg.message_id}: {str(e)}")
            return {
                "message_id": msg.message_id,
                "role": str(getattr(msg, "role", "unknown")),
                "content": "Error: Message content could not be serialized for storage",
                "created_at": datetime.now().isoformat(),
                "error": str(e),
                "citations": [],
                "attachments": [],
            }

    async def _save_messages(self, conversation_id: str, user_id: str, messages: list) -> bool:
        """
        Save messages to the messages container.

        Args:
            conversation_id (str): The ID of the conversation the messages belong to
            user_id (str): The ID of the user who owns this conversation
            messages (list): List of message objects to save

        Returns:
            bool: True if save was successful, False otherwise

        """
        if not messages:
            logger.info(f"No messages to save for conversation '{conversation_id}'")
            return True

        try:
            # First, delete any existing messages for this conversation (for update operations)
            await self._delete_messages(conversation_id)

            # Serialize messages
            serialized_messages = []
            for idx, msg in enumerate(messages):
                try:
                    # Use our enhanced serialization method
                    message_dict = await self._serialize_message(msg)

                    # Add required fields for CosmosDB
                    # Unique ID
                    message_dict["id"] = f"{conversation_id}:{msg.message_id}"
                    # Used as partition key
                    message_dict["conversation_id"] = conversation_id
                    message_dict["user_id"] = user_id
                    # For correct ordering when retrieving
                    message_dict["sequence"] = idx

                    # Final check to ensure serialization works
                    try:
                        json.dumps(message_dict)
                        serialized_messages.append(message_dict)
                    except (TypeError, OverflowError) as json_error:
                        logger.error(
                            f"Message {msg.message_id} failed final JSON serialization check: {str(json_error)}"
                        )
                        # Create a failsafe simplified version
                        failsafe_dict = {
                            "id": f"{conversation_id}:{msg.message_id}",
                            "conversation_id": conversation_id,
                            "user_id": user_id,
                            "sequence": idx,
                            "message_id": str(msg.message_id),
                            "role": str(getattr(msg, "role", "unknown")),
                            "content": "Error: Message content could not be serialized for storage",
                            "created_at": datetime.now().isoformat(),
                            "error": f"JSON serialization error: {str(json_error)}",
                            "citations": [],
                            "attachments": [],
                        }
                        serialized_messages.append(failsafe_dict)
                except Exception as msg_error:
                    logger.error(f"Error processing message {getattr(msg, 'message_id', 'unknown')}: {str(msg_error)}")
                    # Include a placeholder for this message to maintain sequence
                    error_dict = {
                        "id": f"{conversation_id}:error_{idx}",
                        "conversation_id": conversation_id,
                        "user_id": user_id,
                        "sequence": idx,
                        "message_id": f"error_{idx}",
                        "role": "system",
                        "content": "Error: A message in this conversation could not be saved",
                        "created_at": datetime.now().isoformat(),
                        "error": str(msg_error),
                        "citations": [],
                        "attachments": [],
                    }
                    serialized_messages.append(error_dict)

            # Use batch operations if supported, otherwise use individual operations
            loop = asyncio.get_event_loop()

            # Break into smaller batches if needed (recommended max batch size is 100)
            batch_size = 50
            for i in range(0, len(serialized_messages), batch_size):
                batch = serialized_messages[i : i + batch_size]

                # Use individual operations for maximum compatibility
                for message in batch:
                    try:
                        # Final JSON serialization check to ensure we're passing valid data to CosmosDB
                        json.dumps(message)

                        await loop.run_in_executor(None, lambda m=message: self.messages_container.upsert_item(body=m))  # type: ignore[misc]
                    except (TypeError, ValueError, OverflowError) as json_error:
                        logger.error(
                            f"Failed to send message to CosmosDB due to serialization error: {str(json_error)}"
                        )
                        # Create an emergency simplified version and try once more
                        try:
                            emergency_dict = {
                                "id": message.get("id", f"{conversation_id}:emergency_{i}"),
                                "conversation_id": conversation_id,
                                "user_id": user_id,
                                "sequence": message.get("sequence", 9999),
                                "message_id": str(message.get("message_id", f"emergency_{i}")),
                                "role": "system",
                                "content": "Error: Message could not be saved due to serialization issues",
                                "created_at": datetime.now().isoformat(),
                                "error": str(json_error),
                                "citations": [],
                                "attachments": [],
                            }

                            await loop.run_in_executor(
                                None, lambda m=emergency_dict: self.messages_container.upsert_item(body=m)  # type: ignore[misc]
                            )
                        except Exception as final_error:
                            logger.error(f"Even emergency fallback failed: {str(final_error)}")
                    except Exception as cosmos_error:
                        logger.error(f"CosmosDB error inserting message: {str(cosmos_error)}")

            logger.info(f"Saved {len(serialized_messages)} messages for conversation '{conversation_id}'")
            return True

        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"CosmosDB error saving messages for conversation '{conversation_id}': {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving messages: {str(e)}")
            import traceback

            logger.error(traceback.format_exc())
            return False

    async def _delete_messages(self, conversation_id: str) -> bool:
        """
        Delete all messages for a conversation.

        Args:
            conversation_id (str): The ID of the conversation whose messages to delete

        Returns:
            bool: True if deletion was successful, False otherwise

        """
        try:
            logger.info(f"Deleting messages for conversation '{conversation_id}'")

            # Query for all messages for this conversation
            query = f"SELECT c.id FROM c WHERE c.conversation_id = '{conversation_id}'"

            loop = asyncio.get_event_loop()

            # CRITICAL FIX: Ensure we're querying the messages container
            items = await loop.run_in_executor(
                None, lambda: list(self.messages_container.query_items(query=query, partition_key=conversation_id))
            )

            # Delete each message from the messages container
            for item in items:
                await loop.run_in_executor(
                    None,
                    lambda item=item: self.messages_container.delete_item(  # type: ignore[misc]
                        item=item["id"], partition_key=conversation_id
                    ),
                )

            logger.info(f"Deleted {len(items)} messages for conversation '{conversation_id}'")
            return True

        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"CosmosDB error deleting messages for conversation '{conversation_id}': {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting messages: {str(e)}")
            return False

    async def _load_messages(self, conversation_id: str) -> list[dict[str, Any]]:
        """
        Load messages for a conversation from the messages container.

        Args:
            conversation_id (str): The ID of the conversation whose messages to load

        Returns:
            list[dict[str, Any]]: List of message dictionaries, ordered by sequence

        """
        try:
            logger.info(f"Loading messages for conversation '{conversation_id}'")

            # Query for all messages for this conversation, ordered by sequence
            query = f"SELECT * FROM c WHERE c.conversation_id = '{conversation_id}' ORDER BY c.sequence"

            loop = asyncio.get_event_loop()

            # CRITICAL FIX: Ensure we're querying the messages container
            try:
                items = await loop.run_in_executor(
                    None, lambda: list(self.messages_container.query_items(query=query, partition_key=conversation_id))
                )

                # Remove CosmosDB specific fields
                for item in items:
                    if "id" in item:
                        del item["id"]
                    if "sequence" in item:
                        del item["sequence"]

                logger.info(f"Loaded {len(items)} messages for conversation '{conversation_id}'")
                return items
            except exceptions.CosmosHttpResponseError as e:
                logger.error(f"Error querying messages container: {str(e)}")
                return []

        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"CosmosDB error loading messages for conversation '{conversation_id}': {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error loading messages: {str(e)}")
            return []

    async def save_conversation(self, conversation: Conversation, user_id: str) -> bool:
        """
        Save a conversation to CosmosDB with messages in a separate container.

        Args:
            conversation (Conversation): The conversation to save
            user_id (str): The ID of the user who owns this conversation

        Returns:
            bool: True if save was successful, False otherwise

        """
        try:
            # First save messages to messages container
            messages_saved = await self._save_messages(conversation.conversation_id, user_id, conversation.messages)

            if not messages_saved:
                logger.error(f"Failed to save messages for conversation '{conversation.conversation_id}'")
                return False

            # Then save conversation metadata (without messages) to conversation container
            conversation_dict = {
                "id": conversation.conversation_id,  # Required by CosmosDB
                "conversation_id": conversation.conversation_id,
                "user_id": user_id,  # Add user_id for multi-user support and partitioning
                "agent_id": conversation.agent.id,
                "title": conversation.title,
                "created_at": convert_to_isoformat(conversation.created_at),
                "last_updated_at": convert_to_isoformat(conversation.last_updated_at),
                # Store the count instead of the messages
                "message_count": len(conversation.messages),
                "metadata": conversation.metadata,
            }

            # Log the document size to help with debugging
            import json

            doc_size = len(json.dumps(conversation_dict))
            logger.info(f"Saving conversation metadata '{conversation.conversation_id}': {doc_size} bytes")

            # Use the event loop to run synchronous cosmos operation
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: self.conversation_container.upsert_item(body=conversation_dict)
            )

            logger.info(
                f"Conversation metadata '{conversation.conversation_id}' for user '{user_id}' "
                f"saved to CosmosDB. Request charge: {result.get('_ts', 'unknown')}"
            )
            return True

        except exceptions.CosmosHttpResponseError as e:
            logger.error(
                f"CosmosDB error saving conversation '{conversation.conversation_id}' for user '{user_id}': {str(e)}"
            )
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving conversation: {str(e)}")
            import traceback

            logger.error(traceback.format_exc())
            return False

    async def load_conversation(self, conversation_id: str, user_id: str) -> Optional[dict[str, Any]]:
        """
        Load a conversation from CosmosDB, retrieving both metadata and messages.

        Args:
            conversation_id (str): The ID of the conversation to load
            user_id (str): The ID of the user who owns this conversation

        Returns:
            Optional[dict[str, Any]]: The conversation data if found, None otherwise

        """
        try:
            # Using partition key for efficient querying
            try:
                logger.info(f"Attempting to load conversation '{conversation_id}' for user '{user_id}'")
                # First try direct point read using partition key and id for maximum efficiency
                conversation_metadata = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: self.conversation_container.read_item(item=conversation_id, partition_key=user_id)
                )

                # Load messages separately
                messages = await self._load_messages(conversation_id)

                # Combine metadata and messages
                conversation = conversation_metadata.copy()
                conversation["messages"] = messages

                # Remove the CosmosDB specific "id" field if it matches conversation_id
                if "id" in conversation and conversation["id"] == conversation["conversation_id"]:
                    del conversation["id"]

                # Remove message_count as it's redundant with messages list
                if "message_count" in conversation:
                    del conversation["message_count"]

                logger.info(f"Conversation '{conversation_id}' for user '{user_id}' loaded from CosmosDB.")
                return conversation

            except exceptions.CosmosResourceNotFoundError:
                logger.warning(f"Conversation '{conversation_id}' not found by direct lookup, trying query")
                # If direct read fails, try a query with a security filter.
                # This ensures the user can only access their own conversations.
                query = f"SELECT * FROM c WHERE c.conversation_id = '{conversation_id}' AND c.user_id = '{user_id}'"

                items = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: list(
                        self.conversation_container.query_items(
                            query=query, partition_key=user_id  # Use partition key for efficiency
                        )
                    ),
                )

                if not items:
                    logger.warning(f"Conversation '{conversation_id}' for user '{user_id}' not found in CosmosDB.")
                    return None

                # Return the first matching conversation
                conversation_metadata = items[0]  # type: ignore[assignment]

                # Load messages separately
                messages = await self._load_messages(conversation_id)

                # Combine metadata and messages
                conversation = conversation_metadata.copy()
                conversation["messages"] = messages

                # Remove the CosmosDB specific "id" field
                if "id" in conversation and conversation["id"] == conversation["conversation_id"]:
                    del conversation["id"]

                # Remove message_count as it's redundant with messages list
                if "message_count" in conversation:
                    del conversation["message_count"]

                logger.info(f"Conversation '{conversation_id}' for user '{user_id}' loaded from CosmosDB via query.")
                return conversation

        except exceptions.CosmosHttpResponseError as e:
            logger.error(
                f"Failed to load conversation '{conversation_id}' for user '{user_id}' from CosmosDB: {str(e)}"
            )
            return None
        except Exception as e:
            logger.error(f"Unexpected error loading conversation: {str(e)}")
            return None

    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Delete a conversation from CosmosDB, including all messages.

        Args:
            conversation_id (str): The ID of the conversation to delete
            user_id (str): The ID of the user who owns this conversation

        Returns:
            bool: True if deletion was successful, False otherwise

        """
        try:
            logger.info(f"Attempting to delete conversation '{conversation_id}' for user '{user_id}'")

            # First delete messages
            messages_deleted = await self._delete_messages(conversation_id)

            if not messages_deleted:
                logger.error(f"Failed to delete messages for conversation '{conversation_id}'")
                # Continue with deleting the main conversation record anyway

            # Then delete conversation metadata
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.conversation_container.delete_item(
                    item=conversation_id, partition_key=user_id  # Use user_id as partition key
                ),
            )

            logger.info(f"Conversation '{conversation_id}' for user '{user_id}' deleted from CosmosDB.")
            return True

        except exceptions.CosmosResourceNotFoundError:
            logger.warning(
                f"Attempted to delete non-existent conversation '{conversation_id}' for user '{user_id}' from CosmosDB."
            )
            # Still delete messages if they exist
            await self._delete_messages(conversation_id)
            return False
        except exceptions.CosmosHttpResponseError as e:
            logger.error(
                f"Failed to delete conversation '{conversation_id}' for user '{user_id}' from CosmosDB: {str(e)}"
            )
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting conversation: {str(e)}")
            return False

    async def list_conversations(
        self,
        user_id: str,
        filters: Optional[dict[str, Any]] = None,
        page_size: int = 50,
        continuation_token: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        List conversations from CosmosDB with optional filtering and pagination.
        Does not include messages in the results.

        Args:
            user_id (str): The ID of the user whose conversations to list
            filters (Optional[dict[str, Any]]): Optional dictionary of filter conditions
            page_size (int): Number of items to return per page (default: 50)
            continuation_token (Optional[str]): Token for continuation of a previous query

        Returns:
            dict[str, Any]: Dictionary containing:
                - items: List of conversation metadata (without messages)
                - continuation_token: Token for fetching the next page (None if no more pages)
                - total_count: Approximate total count of matching items

        """
        try:
            logger.info(f"Listing conversations for user '{user_id}' with filters {filters}")
            # Initialize filters if None
            if filters is None:
                filters = {}

            # Always include user_id filter for security (users can only access their own conversations)
            filters["user_id"] = user_id

            # Build query with filters
            conditions = []
            for key, value in filters.items():
                if isinstance(value, str):
                    conditions.append(f"c.{key} = '{value}'")
                elif value is None:
                    conditions.append(f"c.{key} = null")
                else:
                    conditions.append(f"c.{key} = {value}")

            # Create the full query
            query = "SELECT * FROM c WHERE " + " AND ".join(conditions)

            # Add ORDER BY for consistent pagination
            query += " ORDER BY c.last_updated_at DESC"

            # Use the event loop to run synchronous cosmos operation
            loop = asyncio.get_event_loop()

            # Get total count for the query (approximate)
            count_query = f"SELECT VALUE COUNT(1) FROM c WHERE {' AND '.join(conditions)}"

            try:
                total_count_result = await loop.run_in_executor(
                    None,
                    lambda: list(
                        self.conversation_container.query_items(
                            query=count_query, partition_key=user_id  # Use partition key for efficiency
                        )
                    ),
                )
                total_count = total_count_result[0] if total_count_result else 0
            except Exception as e:
                logger.warning(f"Error getting count of conversations: {str(e)}")
                total_count = 0

            # Execute the paginated query
            try:
                # Note: Azure Cosmos DB SDK doesn't support passing continuation token directly
                # Continuation tokens are handled through the ItemPaged iterator
                query_result = await loop.run_in_executor(
                    None,
                    lambda: self.conversation_container.query_items(
                        query=query,
                        partition_key=user_id,
                        max_item_count=page_size,
                    ),
                )

                # Get the results and the continuation token
                items = list(query_result)
                # Handle potential continuation token safely
                new_continuation_token = getattr(query_result, "continuation", None)
            except Exception as e:
                logger.error(f"Error executing query: {str(e)}")
                items = []
                new_continuation_token = None

            # Remove CosmosDB specific "id" field from results
            for item in items:
                if "id" in item and item["id"] == item["conversation_id"]:
                    del item["id"]

            result = {"items": items, "continuation_token": new_continuation_token, "total_count": total_count}

            logger.info(f"Listed {len(items)} conversations for user '{user_id}' from CosmosDB with filters {filters}.")
            return result

        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to list conversations for user '{user_id}' from CosmosDB: {str(e)}")
            return {"items": [], "continuation_token": None, "total_count": 0}
        except Exception as e:
            logger.error(f"Unexpected error listing conversations: {str(e)}")
            return {"items": [], "continuation_token": None, "total_count": 0}

    async def reset_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Reset a conversation by removing all messages but keeping the conversation metadata.

        Args:
            conversation_id (str): The ID of the conversation to reset
            user_id (str): The ID of the user whose conversations to list

        Returns:
            bool: True if reset was successful, False otherwise

        """
        try:
            # First, load the conversation metadata (without messages)
            logger.info(f"Resetting conversation '{conversation_id}' for user '{user_id}'")

            # Delete all messages
            await self._delete_messages(conversation_id)

            # Update the conversation metadata to reflect the reset
            try:
                conversation_metadata = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: self.conversation_container.read_item(item=conversation_id, partition_key=user_id)
                )

                # Update last_updated_at and message_count
                conversation_metadata["last_updated_at"] = datetime.now().isoformat()
                conversation_metadata["message_count"] = 0

                # Use the event loop to run synchronous cosmos operation
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None, lambda: self.conversation_container.upsert_item(body=conversation_metadata)
                )

                logger.info(f"Conversation '{conversation_id}' for user '{user_id}' reset in CosmosDB.")
                return True

            except exceptions.CosmosResourceNotFoundError:
                logger.warning(
                    f"Conversation '{conversation_id}' for user '{user_id}' not found in CosmosDB for reset."
                )
                return False

        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to reset conversation '{conversation_id}' for user '{user_id}' in CosmosDB: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error resetting conversation: {str(e)}")
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
            logger.info(f"Appending message to conversation '{conversation_id}'")

            # Get the current message count for sequence number
            try:
                # Query the conversation container to get the message count
                query = f"SELECT c.message_count FROM c WHERE c.conversation_id = '{conversation_id}' AND c.user_id = '{user_id}'"  # noqa: E501

                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, lambda: list(self.conversation_container.query_items(query=query, partition_key=user_id))
                )

                if not result:
                    logger.error(f"Conversation '{conversation_id}' not found for appending message")
                    return False

                current_count = result[0].get("message_count", 0)
                sequence = current_count  # Use current count as the sequence number for the new message
            except Exception as e:
                logger.error(f"Error getting message count: {str(e)}")
                return False

            # Serialize the message
            try:
                # Use our enhanced serialization method
                message_dict = await self._serialize_message(message)

                # Add required fields for CosmosDB
                message_dict["id"] = f"{conversation_id}:{message.message_id}"
                message_dict["conversation_id"] = conversation_id
                message_dict["user_id"] = user_id
                message_dict["sequence"] = sequence

                # Final check to ensure serialization works
                json.dumps(message_dict)
            except Exception as e:
                logger.error(f"Error serializing message for append: {str(e)}")
                return False

            # Insert the single new message
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: self.messages_container.upsert_item(body=message_dict))

            # Update the message count in the conversation metadata
            try:
                # Update the conversation metadata with the new message count
                query = f"SELECT * FROM c WHERE c.conversation_id = '{conversation_id}' AND c.user_id = '{user_id}'"

                result = await loop.run_in_executor(
                    None, lambda: list(self.conversation_container.query_items(query=query, partition_key=user_id))
                )

                if result:
                    conversation_metadata = result[0]
                    conversation_metadata["message_count"] = current_count + 1
                    conversation_metadata["last_updated_at"] = datetime.now().isoformat()

                    await loop.run_in_executor(
                        None, lambda: self.conversation_container.upsert_item(body=conversation_metadata)
                    )
            except Exception as e:
                logger.error(f"Error updating conversation metadata after append: {str(e)}")
                # Don't return False here as the message was successfully added

            logger.info(f"Successfully appended message to conversation '{conversation_id}'")
            return True

        except Exception as e:
            logger.error(f"Error appending message to conversation '{conversation_id}': {str(e)}")
            return False


def convert_to_isoformat(obj: Any) -> Any:
    """
    Check if the object is a datetime instance and return its ISO format.

    Args:
        obj (Any): The object to check

    Returns:
        Any: The ISO format of the datetime object or the original object

    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj
