"""Abstract Conversation Service for integrating agents with persistence strategies."""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from core.agents.abstract_agent import AbstractAgent
from core.common import GraphAttachment, GraphType, MediaAttachment, MediaType, Message
from core.persistence import Conversation, PersistenceStrategy

logger = logging.getLogger(__name__)


class ConversationService:
    """Abstract base class for conversation services."""

    def __init__(
        self,
        persistence_strategy: PersistenceStrategy,
        agents: Optional[Dict[str, AbstractAgent]] = None,
    ):
        self.persistence_strategy = persistence_strategy
        self._agents = agents or {}
        logger.info(
            f"Initialized {self.__class__.__name__} with "
            f"{self.persistence_strategy.__class__.__name__ if self.persistence_strategy else 'NoPersistence'}"
        )

    def get_agent_instance(self, agent_id: str) -> Optional[AbstractAgent]:
        """
        Retrieve an agent instance by its ID.

        Args:
            agent_id (str): The agent ID.

        Returns:
            Optional[AbstractAgent]: The agent instance if found, else None.

        """
        agent = self._agents.get(agent_id)
        return agent if agent else None

    def get_available_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about available agents.

        Returns:
            Dict[str, Dict[str, Any]]: Information about available agents.

        """
        return {
            agent_id: {
                "name": agent.name,
                "description": getattr(agent, "description", ""),
                "instance": agent,
            }
            for agent_id, agent in self._agents.items()
        }

    async def create_conversation(
        self, agent: AbstractAgent, user_id: str, title: Optional[str] = None
    ) -> Conversation:
        """
        Create a new conversation.

        Args:
            agent (AbstractAgent): The agent instance.
            user_id (str): The user ID.
            title (Optional[str]): The conversation title.

        Returns:
            Conversation: The created conversation.

        Raises:
            RuntimeError: If the conversation could not be saved.

        """
        conversation_id = str(uuid.uuid4())
        now = datetime.now()
        if title is None:
            title = f"Conversation with {agent.name}"
        if agent.id not in self._agents:
            self._agents[agent.id] = agent
        conversation = Conversation(
            conversation_id=conversation_id,
            agent=agent,
            title=title,
            created_at=now,
            last_updated_at=now,
            messages=[],
            metadata={"user_id": user_id},
        )
        success = await self.persistence_strategy.save_conversation(conversation, user_id)
        if not success:
            logger.error(f"Failed to save new conversation {conversation_id} for user {user_id}")
            raise RuntimeError(f"Failed to save conversation {conversation_id}")
        logger.info(f"Created new conversation {conversation_id} for user {user_id} with agent {agent.id}")
        return conversation

    async def create_conversation_by_agent_id(
        self, agent_id: str, user_id: str, title: Optional[str] = None
    ) -> Conversation:
        """
        Create a new conversation.

        Args:
            agent_id (str): The agent ID.
            user_id (str): The user ID.
            title (Optional[str]): The conversation title.

        Returns:
            Conversation: The created conversation.

        Raises:
            RuntimeError: If the conversation could not be saved.
            ValueError: If the agent is not available.

        """
        agent = self.get_agent_instance(agent_id)
        if agent is None:
            logger.error(f"Agent {agent_id} not found for user {user_id}")
            raise ValueError(f"Agent {agent_id} not available")
        conversation_id = str(uuid.uuid4())
        now = datetime.now()
        if title is None:
            title = f"Conversation with {agent.name}"
        conversation = Conversation(
            conversation_id=conversation_id,
            agent=agent,
            title=title,
            created_at=now,
            last_updated_at=now,
            messages=[],
            metadata={"user_id": user_id},
        )
        success = await self.persistence_strategy.save_conversation(conversation, user_id)
        if not success:
            logger.error(f"Failed to save new conversation {conversation_id} for user {user_id}")
            raise RuntimeError(f"Failed to save conversation {conversation_id}")
        logger.info(f"Created new conversation {conversation_id} for user {user_id} with agent {agent.id}")
        return conversation

    async def send_message(
        self, conversation_id: str, user_id: str, message_content: str, context: Optional[Dict[str, Any]] = None
    ) -> Message:
        """
        Send a message in a conversation.

        Args:
            conversation_id (str): The conversation ID.
            user_id (str): The user ID.
            message_content (str): The message content.
            context (Optional[Dict[str, Any]]): Additional context.

        Returns:
            Message: The agent's response message.

        Raises:
            ValueError: If the conversation or agent is not found.

        """
        conversation_data = await self.persistence_strategy.load_conversation(conversation_id, user_id)
        if not conversation_data:
            logger.error(f"Conversation {conversation_id} not found for user {user_id}")
            raise ValueError(f"Conversation {conversation_id} not found")
        user_message = Message(
            message_id=str(uuid.uuid4()),
            role="user",
            content=message_content,
            created_at=datetime.now().isoformat(),
            citations=[],
            metadata={"user_id": user_id},
            attachments=[],
        )
        await self.persistence_strategy.append_message(conversation_id, user_id, user_message)
        agent_id = conversation_data.get("agent_id")
        agent = self.get_agent_instance(agent_id)
        if agent is None:
            logger.error(f"Failed to instantiate agent {agent_id} for conversation {conversation_id}")
            raise ValueError(f"Agent {agent_id} not available")
        messages = []
        if "messages" in conversation_data:
            messages = conversation_data["messages"]
            agent.update_chat_history(messages)
        agent_response = await agent.process(message_content, context)
        await self.persistence_strategy.append_message(conversation_id, user_id, agent_response)
        updated_conversation_data = await self.persistence_strategy.load_conversation(conversation_id, user_id)
        if not updated_conversation_data:
            logger.error(f"Conversation {conversation_id} not found after appending messages for user {user_id}")
            raise ValueError(f"Conversation {conversation_id} not found after update")
        updated_conversation_data["last_updated_at"] = datetime.now().isoformat()
        await self.persistence_strategy.save_conversation(
            self._create_conversation_from_data(updated_conversation_data, agent), user_id
        )
        logger.info(f"Processed message in conversation {conversation_id} for user {user_id}")
        return agent_response

    async def load_conversation(self, conversation_id: str, user_id: str) -> Optional[Conversation]:
        """
        Load a conversation by its ID.

        Args:
            conversation_id (str): The conversation ID.
            user_id (str): The user ID.

        Returns:
            Optional[Conversation]: The loaded conversation, or None if not found.

        """
        conversation_data = await self.persistence_strategy.load_conversation(conversation_id, user_id)
        if not conversation_data:
            logger.warning(f"Conversation {conversation_id} not found for user {user_id}")
            return None
        agent_id = conversation_data.get("agent_id")
        agent = self.get_agent_instance(agent_id)
        if agent is None:
            logger.error(f"Failed to instantiate agent for conversation {conversation_id}")
            return None
        conversation = self._create_conversation_from_data(conversation_data, agent)
        logger.info(f"Loaded conversation {conversation_id} for user {user_id}")
        return conversation

    async def list_conversations(
        self,
        user_id: str,
        filters: Optional[Dict[str, Any]] = None,
        page_size: Optional[int] = 50,
        continuation_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List conversations for a user.

        Args:
            user_id (str): The user ID.
            filters (Optional[Dict[str, Any]]): Filters for the conversations.
            page_size (Optional[int]): Number of conversations per page.
            continuation_token (Optional[str]): Token for pagination.

        Returns:
            Dict[str, Any]: The list of conversations.

        """
        result = await self.persistence_strategy.list_conversations(user_id, filters, page_size, continuation_token)
        logger.info(f"Listed {len(result['items'])} conversations for user {user_id}")
        return result

    async def reset_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Reset a conversation.

        Args:
            conversation_id (str): The conversation ID.
            user_id (str): The user ID.

        Returns:
            bool: True if successful, False otherwise.

        """
        success = await self.persistence_strategy.reset_conversation(conversation_id, user_id)
        if success:
            logger.info(f"Reset conversation {conversation_id} for user {user_id}")
        else:
            logger.error(f"Failed to reset conversation {conversation_id} for user {user_id}")
        return success

    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Delete a conversation.

        Args:
            conversation_id (str): The conversation ID.
            user_id (str): The user ID.

        Returns:
            bool: True if successful, False otherwise.

        """
        success = await self.persistence_strategy.delete_conversation(conversation_id, user_id)
        if success:
            logger.info(f"Deleted conversation {conversation_id} for user {user_id}")
        else:
            logger.error(f"Failed to delete conversation {conversation_id} for user {user_id}")
        return success

    def _create_conversation_from_data(self, conversation_data: Dict[str, Any], agent: AbstractAgent) -> Conversation:
        """
        Create a conversation object from data.

        Args:
            conversation_data (Dict[str, Any]): The conversation data.
            agent (AbstractAgent): The agent instance.

        Returns:
            Conversation: The created conversation object.

        """
        messages = []
        if "messages" in conversation_data:
            raw_messages = conversation_data["messages"]
            for msg_data in raw_messages:
                formatted_attachments = []
                attachments = msg_data.get("attachments", [])
                if len(attachments) > 0:
                    user_id = conversation_data.get("user_id")
                    for attachment in attachments:
                        logger.debug(f"Attachment: {attachment}", extra={"user": user_id})
                        if "type" in attachment:
                            type = attachment["type"]["_name_"]
                            if type in GraphType.__members__:
                                formatted_attachments.append(
                                    GraphAttachment(
                                        type=GraphType[type],
                                        dataset_json=attachment["dataset_json"],
                                        data_description=attachment["data_description"],
                                        x=attachment["x"],
                                        y=attachment["y"],
                                    )
                                )
                            elif type in MediaType.__members__:
                                formatted_attachments.append(
                                    MediaAttachment(
                                        type=MediaType[type],
                                        content=attachment["content"],
                                        data_description=attachment["data_description"],
                                        start_time=attachment["start_time"],
                                        autoplay=attachment["autoplay"],
                                        loop=attachment["loop"],
                                    )
                                )
                        else:
                            message_id = msg_data.get("message_id", str(uuid.uuid4()))
                            logger.warning(
                                "Failed to load attachment. This object does not have 'type'."
                                "Please check the attachment in database: "
                                f"MessageID {message_id} and Attachment {attachment}",
                                extra={"user": user_id},
                            )
                message = Message(
                    message_id=msg_data.get("message_id", str(uuid.uuid4())),
                    role=msg_data.get("role", "system"),
                    content=msg_data.get("content", ""),
                    created_at=msg_data.get("created_at", datetime.now().isoformat()),
                    citations=msg_data.get("citations", []),
                    metadata=msg_data.get("metadata", {}),
                    attachments=formatted_attachments,
                )
                messages.append(message)
        created_at = conversation_data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        else:
            created_at = datetime.now()
        last_updated_at = conversation_data.get("last_updated_at")
        if isinstance(last_updated_at, str):
            last_updated_at = datetime.fromisoformat(last_updated_at)
        else:
            last_updated_at = datetime.now()
        return Conversation(
            conversation_id=conversation_data.get("conversation_id"),
            agent=agent,
            title=conversation_data.get("title", f"Conversation with {agent.name}"),
            created_at=created_at,
            last_updated_at=last_updated_at,
            messages=messages,
            metadata=conversation_data.get("metadata", {}),
        )
