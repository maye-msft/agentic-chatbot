"""Defines the AbstractLlamaIndexAgent class and its associated methods."""

import inspect
import logging
import os
import uuid
from abc import ABC
from datetime import datetime
from typing import Any, Optional, Union, cast

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.core.agent import ReActAgent
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms import LLM
from llama_index.core.tools import FunctionTool
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.llms.azure_openai import AzureOpenAI
from opentelemetry import trace

from core.agents.abstract_agent import AbstractAgent
from core.common import GraphAttachment, MediaAttachment, Message, ResponseWithAttachments
from core.tools import Tool

# from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding


load_dotenv(override=True)

# Configure logging
logger = logging.getLogger("agentic_chatbot")
tracer = trace.get_tracer(__name__)

# Static variables
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_BASE_URL = os.environ.get("AZURE_OPENAI_BASE_URL")
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
AZURE_OPENAI_EMBEDDING_ENDPOINT = os.environ.get("AZURE_OPENAI_EMBEDDING_ENDPOINT")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "local")

# Set up the bearer token provider for MID authentication
token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")


class AbstractLlamaIndexAgent(AbstractAgent, ABC):
    """
    AbstractLlamaIndexAgent is a specialized agent that integrates LlamaIndex capabilities.

    This class provides methods to configure and utilize LlamaIndex agents,
    as well as manage chat history and tool usage.
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        prompt: str,
        tools: dict[str, Tool],
        settings: Optional[dict[str, Any]] = None,
    ):
        super().__init__(agent_id, name, description, prompt, tools, settings)

        # Initialize LlamaIndex settings
        self._configure_llama_index_settings()

        # Initialize instance variables
        self._tool_usage: list[Tool] = []
        self._chat_history: list[dict[str, Any]] = []
        self._attachments: list[Union[MediaAttachment, GraphAttachment]] = []

        # Set maximum history length (default to 20 if not specified)
        self._max_history_length = settings.get("max_history_length", 20) if settings else 20
        logger.info(f"Setting max history length to: {self._max_history_length}")

        # Create the LlamaIndex agent
        self._agent = self._create_agent(tools)

    def _configure_llama_index_settings(self) -> None:
        """Configure the global LlamaIndex settings."""
        llm = self._get_llm()
        embed_model = self._get_embedding_model()

        # Configure global settings
        Settings.llm = llm
        Settings.embed_model = embed_model
        Settings.chunk_size = 1024

    def _get_llm(self) -> LLM:
        """
        Get the LLM model to use for the agent.

        Returns:
            LLM: An instance of LLM.

        """
        # Switch client based on environment
        return AzureOpenAI(
            engine=AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
            model=AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
            api_key=AZURE_OPENAI_API_KEY,
            azure_endpoint=AZURE_OPENAI_BASE_URL,
            api_version=AZURE_OPENAI_API_VERSION,
            temperature=0.1,
        )

    def _get_embedding_model(self) -> BaseEmbedding:
        """
        Get the embedding model to use for the agent.

        Returns:
            BaseEmbedding: An instance of BaseEmbedding.

        """
        # Switch client based on environment
        return AzureOpenAIEmbedding(
            model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
            api_key=AZURE_OPENAI_API_KEY,
            azure_endpoint=AZURE_OPENAI_EMBEDDING_ENDPOINT,
            api_version=AZURE_OPENAI_API_VERSION,
        )

    def _create_agent(self, tools: dict[str, Tool]) -> ReActAgent:
        """
        Create a LlamaIndex ReActAgent with the provided tools.

        Args:
            tools (dict[str, Tool]): Dictionary of tools to add to the agent.

        Returns:
            ReActAgent: A ReActAgent instance.

        """
        # Convert our tools to LlamaIndex tools
        llama_tools = self._convert_tools_to_llama_tools(tools)

        # Create the agent without explicit memory config
        # We'll manage conversation context manually
        agent = ReActAgent.from_tools(tools=llama_tools, llm=self._get_llm(), system_prompt=self.prompt, verbose=True)
        return agent

    def _convert_tools_to_llama_tools(self, tools: dict[str, Tool]) -> list[FunctionTool]:
        """
        Convert our Tool objects to LlamaIndex Tool objects.

        Args:
            tools (dict[str, Tool]): Dictionary of our Tool objects.

        Returns:
            list[FunctionTool]: List of LlamaIndex Tool objects.

        """
        llama_tools = []

        for tool in tools.values():
            # Create a LlamaIndex FunctionTool from our Tool
            llama_tool = FunctionTool.from_defaults(
                fn=self._build_tool(tool), name=tool.name, description=tool.description
            )
            llama_tools.append(llama_tool)

        return llama_tools

    def _build_tool(self, tool: Tool) -> Any:
        signature = inspect.signature(tool.function)

        def function_wrapper(*args: Any, **kwargs: Any) -> Any:
            with tracer.start_as_current_span(
                f"[agentic_chatbot.tool] run: {tool.name}", context=trace.get_current_span().get_span_context()
            ) as span:
                span.set_attribute("tool_name", tool.name)
                span.set_attribute("tool_description", tool.description)
                span.set_attribute("args", args)
                span.set_attributes(kwargs)

                try:
                    start_time = datetime.now()
                    result = tool.function(*args, **kwargs)
                    end_time = datetime.now()
                    elapsed_time = end_time - start_time

                    span.set_attribute("tool_response", str(result))

                    # Record tool usage
                    self._tool_usage.append(
                        {
                            "tool_name": tool.name,
                            "args": args,
                            "kwargs": kwargs,
                            "result": result,
                            "start_time": start_time.isoformat(),
                            "duration": elapsed_time.microseconds,
                        }
                    )

                    # Handle ResponseWithAttachments
                    if issubclass(type(result), ResponseWithAttachments):
                        self._attachments.extend(result.attachments)
                except Exception as e:
                    span.set_attribute("error", str(e))
                    logger.error(f"Error executing tool '{tool.name}': {str(e)}")
                    raise

                return result

        function_wrapper = cast(Any, function_wrapper)
        function_wrapper.__signature__ = signature  # type: ignore[attr-defined]

        return function_wrapper

    def _record_tool_usage(self, tool_name: str, args: Any, result: Any) -> None:
        """
        Record the usage of a tool for tracking purposes.

        Args:
            tool_name (str): Name of the tool used.
            args (Any): Arguments passed to the tool.
            result (Any): Result returned by the tool.

        """
        start_time = datetime.now()

        self._tool_usage.append(
            {
                "tool_name": tool_name,
                "args": args,
                "result": result,
                "start_time": start_time.isoformat(),
                "duration": 0,  # This would be calculated in a real implementation
            }
        )

    def _prune_chat_history(self) -> None:
        """Prune the chat history to ensure it never exceeds the maximum length."""
        if len(self._chat_history) >= self._max_history_length:
            logger.info(f"Pruning chat history from {len(self._chat_history)} to {self._max_history_length} messages")

            # Always preserve system messages
            system_messages = [msg for msg in self._chat_history if msg.get("role") == "system"]

            # Calculate how many other messages we can keep
            remaining_slots = max(0, self._max_history_length - len(system_messages))

            # Get most recent non-system messages
            non_system_messages = [msg for msg in self._chat_history if msg.get("role") != "system"]
            recent_messages = non_system_messages[-remaining_slots:] if remaining_slots > 0 else []

            # Update chat history
            self._chat_history = system_messages + recent_messages

            # Verify length
            logger.info(f"After pruning: {len(self._chat_history)} messages")

    async def process(self, message: str, context: Optional[dict[str, Any]] = None) -> Message:
        """
        Process a user message and generate a response using the agent.

        Args:
            message (str): The user message to process.
            context (Optional[dict[str, Any]]): Optional additional context for processing.

        Returns:
            Message: A Message object containing the agent's response.

        """
        with tracer.start_as_current_span(f"[agentic_chatbot.agent] process: {self.name}") as span:
            span.set_attribute("agent", "llma_index")
            span.set_attribute("message", message)

            logger.info(f"Processing message with agent '{self.name}' with ID '{self.id}'")

            # Reset tool usage tracking
            self._tool_usage = []
            self._attachments = []

            # Prune history before adding new message
            self._prune_chat_history()

            # Add the user message to chat history
            self._chat_history.append({"role": "user", "content": message})

            # Process the message with the LlamaIndex agent
            try:
                # Construct a prompt with chat history context
                chat_context = ""
                if len(self._chat_history) > 1:  # If there's more than just the current message
                    # Get previous messages except the current one
                    prev_messages = self._chat_history[:-1]
                    for msg in prev_messages:
                        role = msg.get("role", "")
                        content = msg.get("content", "")
                        if role and content:
                            # Format nicely for the agent
                            if role == "user":
                                chat_context += f"User: {content}\n"
                            elif role == "assistant":
                                chat_context += f"Assistant: {content}\n"
                            elif role == "system":
                                # System messages are typically handled in the system prompt
                                continue

                # If we have chat context, include it in the query
                query = message
                if chat_context:
                    query = (
                        f"Chat history:\n{chat_context}\n"
                        f"Current question: {message}\n"
                        f"Please respond to the current question considering the chat history for context."
                    )

                response = await self._agent.aquery(query)
                response_text = str(response)

                span.set_attribute("response", response_text)

                # Add the assistant response to chat history
                self._chat_history.append({"role": "assistant", "content": response_text})

                # Create a Message object with the response
                return Message(
                    message_id=str(uuid.uuid4()),
                    role="assistant",
                    content=response_text,
                    created_at=datetime.now().isoformat(),
                    citations=[],
                    metadata={"tool_usage": self._tool_usage.copy()},
                    attachments=self._attachments,
                )
            except Exception as e:
                span.set_attribute("error", str(e))
                logger.error(f"Error processing message: {str(e)}")
                return Message(
                    message_id=str(uuid.uuid4()),
                    role="assistant",
                    content=f"I encountered an error while processing your message: {str(e)}",
                    created_at=datetime.now().isoformat(),
                    citations=[],
                    metadata={"error": str(e)},
                    attachments=[],
                )

    def initialize(self) -> None:
        """Initialize the agent and its resources."""
        logger.info(f"Initializing LlamaIndex agent '{self.name}' with ID '{self.id}'")
        # Any additional initialization logic can go here

    def add_tool(self, tool: Tool) -> None:
        """
        Add a tool to the agent's toolkit.

        Args:
            tool (Tool): The Tool object to add.

        Raises:
            ValueError: If the tool already exists in the agent's toolkit.

        """
        if tool.name not in self._tools:
            self._tools[tool.name] = tool

            # Create a LlamaIndex tool from our Tool
            llama_tool = FunctionTool.from_defaults(
                fn=self._build_tool(tool), name=tool.name, description=tool.description
            )

            # Add the tool to the agent
            self._agent.add_tool(llama_tool)  # type: ignore[attr-defined]

            logger.info(f"Added tool '{tool.name}' to agent '{self.name}'")
        else:
            logger.error(f"Tool '{tool.name}' already exists in agent '{self.name}'")
            raise ValueError(f"Tool '{tool.name}' already exists in agent '{self.name}'")

    def reset_conversation(self) -> None:
        """Reset the conversation state for the agent."""
        logger.info(f"Resetting conversation for agent '{self.name}' with ID '{self.id}'")
        self._chat_history = []
        self._tool_usage = []
        self._attachments = []

        # Recreate the agent to reset its internal state and memory
        self._agent = self._create_agent(self._tools)

    def update_chat_history(self, messages: list[dict[str, Any] | Message]) -> None:
        """
        Update the chat history with new messages.

        Args:
            messages (list[dict[str, Any] | Message]): List of messages to add to the chat history.

        """
        logger.info(f"Updating chat history for agent '{self.name}' with ID '{self.id}'")

        # Ensure we don't exceed the maximum history length
        self._prune_chat_history()

        # Add the messages to the chat history
        for message in messages:
            if isinstance(message, Message):
                self._chat_history.append(
                    {"role": message.role, "content": message.content, "created_at": message.created_at}
                )
            else:
                self._chat_history.append(message)
