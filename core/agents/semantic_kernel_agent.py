"""Defines the AbstractSemanticKernelAgent class and its associated methods."""

import inspect
import logging
import os
import uuid
from abc import ABC
from datetime import datetime
from typing import Any, Optional, Union

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from openai.lib.azure import AsyncAzureOpenAI
from opentelemetry import trace
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.functions.kernel_function_from_method import KernelFunctionFromMethod
from semantic_kernel.functions.kernel_plugin import KernelPlugin

from core.agents.abstract_agent import AbstractAgent
from core.common import GraphAttachment, MediaAttachment, Message, ResponseWithAttachments
from core.tools import Tool

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


class AbstractSemanticKernelAgent(AbstractAgent, ABC):
    """
    AbstractSemanticKernelAgent is a specialized agent that integrates Semantic Kernel capabilities.

    This class provides methods to configure and utilize chat completion and text embedding services,
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

        # Create a semantic kernel
        kernel = Kernel()

        # Allow the kernel to use chat completion service
        kernel = self.allow_chat_completion(kernel, service_id=agent_id)

        # Allow the kernel to use text embedding service
        kernel = self.allow_text_embedding(kernel)

        # Initialize
        self._kernel = kernel
        self._tool_usage: list[Tool] = []
        self._chat = ChatHistory()
        self._attachments: list[Union[MediaAttachment, GraphAttachment]] = []

        # Set maximum history length (default to 20 if not specified)
        self._max_history_length = settings.get("max_history_length", 20) if settings else 20
        logger.info(f"Setting max history length to: {self._max_history_length}")

        # Add the plugin
        if tools:
            self._add_plugin(tools)

        execution_settings = kernel.get_prompt_execution_settings_from_service_id(service_id=agent_id)
        execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

        if settings:
            if "maximum_auto_invoke_attempts" in settings:
                execution_settings.function_choice_behavior.maximum_auto_invoke_attempts = int(
                    settings["maximum_auto_invoke_attempts"]
                )

        # Create the agent
        self._agent = ChatCompletionAgent(
            id=agent_id,
            kernel=kernel,
            arguments=KernelArguments(settings=execution_settings),
            name=agent_id,
            instructions=prompt,
        )

    @staticmethod
    def allow_chat_completion(
        kernel: Kernel,
        service_id: str,
        async_openai_client: Optional[AsyncAzureOpenAI] = None,
        chat_completion: Optional[AzureChatCompletion] = None,
    ) -> Kernel:
        """
        Configure the kernel to use a chat completion service.

        Args:
            kernel (Kernel): The Semantic Kernel instance to configure.
            service_id (str): The unique identifier for the service.
            async_openai_client (Optional[AsyncAzureOpenAI]): Optional AsyncAzureOpenAI client for chat completion.
            chat_completion (Optional[AzureChatCompletion]): Optional AzureChatCompletion instance.

        Returns:
            Kernel: The configured Semantic Kernel instance.

        Raises:
            Exception: If the environment is not set to 'local', 'demo', or 'sandbox'.

        """
        if chat_completion is None:
            if async_openai_client is None:
                # Switch client based on environment
                if ENVIRONMENT == "local":
                    async_openai_client = AsyncAzureOpenAI(
                        api_key=AZURE_OPENAI_API_KEY,
                        azure_endpoint=AZURE_OPENAI_BASE_URL,
                        api_version=AZURE_OPENAI_API_VERSION,
                    )
                elif ENVIRONMENT == "demo" or ENVIRONMENT == "sandbox":
                    async_openai_client = AsyncAzureOpenAI(
                        api_version=AZURE_OPENAI_API_VERSION,
                        azure_endpoint=AZURE_OPENAI_BASE_URL,
                        azure_ad_token_provider=token_provider,
                    )
                else:
                    raise Exception("Invalid environment. Please set the environment to 'local', 'demo', or 'sandbox'.")
            # Create the chat completion service with the async client
            chat_completion = AzureChatCompletion(
                async_client=async_openai_client,
                service_id=service_id,
            )

        kernel.add_service(chat_completion)
        return kernel

    @staticmethod
    def allow_text_embedding(kernel: Kernel, embedding_gen: Optional[AzureTextEmbedding] = None) -> Kernel:
        """
        Configure the kernel to use a text embedding service.

        Args:
            kernel (Kernel): The Semantic Kernel instance to configure.
            embedding_gen (Optional[AzureTextEmbedding]): Optional AzureTextEmbedding instance.

        Returns:
            Kernel: The configured Semantic Kernel instance.

        Raises:
            Exception: If the environment is not set to 'local', 'demo', or 'sandbox'.

        """
        if embedding_gen is None:
            # Switch client based on environment
            if ENVIRONMENT == "local":
                embedding_gen = AzureTextEmbedding(
                    api_key=AZURE_OPENAI_API_KEY,
                    service_id="embedding",
                    deployment_name=AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
                    endpoint=AZURE_OPENAI_EMBEDDING_ENDPOINT,
                )
            elif ENVIRONMENT == "demo" or ENVIRONMENT == "sandbox":
                embedding_gen = AzureTextEmbedding(
                    service_id="embedding",  # this should be replaced with the model name?
                    deployment_name=AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
                    endpoint=AZURE_OPENAI_EMBEDDING_ENDPOINT,
                    ad_token_provider=token_provider,
                )
            else:
                raise Exception("Invalid environment. Please set the environment to 'local', 'demo', or 'sandbox'.")
        kernel.add_service(embedding_gen)
        return kernel

    def _add_plugin(self, tools: dict[str, Tool]) -> None:
        """
        Add a plugin to the kernel using the provided tools.

        Args:
            tools (dict[str, Tool]): Dictionary of tools to add as plugins.

        """
        functions = []
        for tool in tools.values():
            build_func = self._build_func(tool)

            function = KernelFunctionFromMethod(
                method=kernel_function(build_func, tool.name, tool.description), plugin_name=tool.name
            )
            functions.append(function)

        self._kernel.add_plugin(KernelPlugin(name="plugin", functions=functions))

    def _build_func(self, tool: Tool) -> Any:
        """
        Build a function for the given tool.

        Args:
            tool (Tool): The tool to build the function for.

        Returns:
            Any: The built function.

        """

        async def new_plugin_func(*args: Any, **kwargs: Any) -> Any:
            with tracer.start_as_current_span(f"[agentic_chatbot.tool] run: {tool.name}") as span:
                span.set_attribute("tool_name", tool.name)
                span.set_attribute("tool_description", tool.description)
                span.set_attribute("args", args)
                span.set_attributes(kwargs)

                resp = None

                start_time = datetime.now()
                if inspect.iscoroutinefunction(tool.function):
                    resp = await tool.function(*args, **kwargs)
                else:
                    resp = tool.function(*args, **kwargs)
                end_time = datetime.now()
                elapsed_time = end_time - start_time

                self._tool_usage.append(
                    {
                        "tool_name": tool.name,
                        "args": args,
                        "kwargs": kwargs,
                        "result": resp,
                        "start_time": start_time.isoformat(),
                        "duration": elapsed_time.microseconds,
                    }
                )

                if issubclass(type(resp), ResponseWithAttachments):
                    self._attachments.extend(resp.attachments)

                span.set_attribute("tool_response", str(resp))
                return resp

        # Update the signature of the new function
        plugin_func = kernel_function(tool.function, tool.name, tool.description)
        signature = inspect.signature(plugin_func)
        new_plugin_func.__signature__ = signature  # type: ignore[attr-defined]

        return new_plugin_func

    def _prune_chat_history(self) -> None:
        """Prune the chat history to ensure it never exceeds the maximum length."""
        if len(self._chat.messages) >= self._max_history_length:
            logger.info(f"Pruning chat history from {len(self._chat.messages)} to {self._max_history_length} messages")

            # Always preserve system messages
            system_messages = [msg for msg in self._chat.messages if msg.role == "system"]

            # Calculate how many other messages we can keep
            remaining_slots = max(0, self._max_history_length - len(system_messages))

            # Get most recent non-system messages
            non_system_messages = [msg for msg in self._chat.messages if msg.role != "system"]
            recent_messages = non_system_messages[-remaining_slots:] if remaining_slots > 0 else []

            # Create new chat history with preserved system messages + recent messages
            new_chat = ChatHistory()

            # Add all messages in proper order
            for msg in system_messages + recent_messages:
                if msg.role == "system":
                    new_chat.add_system_message(msg.content)
                elif msg.role == "user":
                    new_chat.add_user_message(msg.content)
                elif msg.role == "assistant":
                    new_chat.add_assistant_message(msg.content)

            # Replace old chat history
            self._chat = new_chat

            # Verify length
            logger.info(f"After pruning: {len(self._chat.messages)} messages")

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
            span.set_attribute("agent_id", self._agent.id)
            span.set_attribute("agent_name", self._agent.name)
            if self._agent.description:
                span.set_attribute("agent_description", self._agent.description)
            span.set_attribute("message", message)

            self._tool_usage = []
            self._attachments = []

            # Prune history before adding new message to maintain history length
            self._prune_chat_history()

            self._chat.add_user_message(message)

            responses = []
            async for response in self._agent.invoke(messages=self._chat):
                self._chat.add_message(response.message)
                responses.append(str(response.message.content))

            span.set_attribute("response", responses)

            # deep copy the tool usage to avoid modifying the original tool usage
            tool_usage_copy = self._tool_usage.copy()
            return Message(
                message_id=str(uuid.uuid4()),
                role="assistant",
                content="\n".join(responses),
                created_at=datetime.now().isoformat(),
                citations=[],
                metadata={"tool_usage": tool_usage_copy},
                attachments=self._attachments,
            )

    def reset_conversation(self) -> None:
        """Reset the conversation history."""
        self._chat.clear()

    def update_chat_history(self, messages: list[dict[str, Any] | Message]) -> None:
        """
        Update the agent's internal chat history with messages loaded from persistence.

        Applies history length limit.

        Args:
            messages (list[dict[str, Any] | Message]): List of message dictionaries with role, content, etc.

        """
        # Clear current chat history
        self._chat.clear()

        # Separate system and non-system messages
        system_messages = [msg for msg in messages if self._get_message_prop(msg, "role") == "system"]
        non_system_messages = [msg for msg in messages if self._get_message_prop(msg, "role") != "system"]

        # Limit non-system messages to most recent ones
        limit = max(0, self._max_history_length - len(system_messages))
        recent_non_system = non_system_messages[-limit:] if limit > 0 else []

        # Combine and sort by created_at
        messages_to_add = system_messages + recent_non_system
        try:
            messages_to_add.sort(key=lambda msg: self._get_message_prop(msg, "created_at"))
        except Exception:
            pass

        # Add messages to chat history in the correct order
        for msg in messages_to_add:
            role = self._get_message_prop(msg, "role")
            content = self._get_message_prop(msg, "content")
            if role == "user":
                self._chat.add_user_message(content)
            elif role == "agent" or role == "assistant":
                self._chat.add_assistant_message(content)
            elif role == "system":
                self._chat.add_system_message(content)

        # Reset tool usage tracking
        self._tool_usage = []
        self._attachments = []

        logger.info(
            (
                f"Updated agent chat history with {len(messages_to_add)} of {len(messages)} messages "
                f"(limit: {self._max_history_length})"
            )
        )

    def _get_message_prop(self, msg: dict[str, Any] | Message, prop: str) -> Any:
        """
        Get the specified property from a message.

        Args:
            msg (dict[str, Any] | Message): The message object or dictionary
            prop (str): The property to retrieve

        Returns:
            Any: The value of the specified property

        """
        if isinstance(msg, Message):
            return getattr(msg, prop)
        else:
            return msg.get(prop, "")
