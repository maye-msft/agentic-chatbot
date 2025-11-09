"""Core Abstract tools for the MACS project."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from core.common import Citation, FileRequest, Message, ResponseWithAttachments


class Tool(ABC):
    """Abstract base class representing a generic tool that an agent can use."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique name of the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a brief description of the tool."""
        pass

    @property
    @abstractmethod
    def function(self) -> Callable:
        """Return the function that implements the tool."""
        pass

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of the tool."""
        pass


class AbstractTool(Tool):
    """Abstract base class for tools."""

    def __init__(self, name: str, description: str, function: Callable):
        self._name = name
        self._description = description
        self._function = function

    @property
    def name(self) -> str:
        """
        Get the name of the tool.

        Returns:
            str: The name of the tool.

        """
        return self._name

    @property
    def description(self) -> str:
        """
        Get the description of the tool.

        Returns:
            str: The description of the tool.

        """
        return self._description

    @property
    def function(self) -> Callable:
        """
        Execute the tool's function.

        Returns:
            Callable: The function associated with the tool.

        """
        return self._function

    @property
    def function_signature(self) -> dict[str, Any]:
        """
        Get the function signature (parameters and annotations).

        Returns:
            dict[str, Any]: A dictionary containing the function's parameters and their annotations.

        """
        return self._function.__annotations__

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the tool to a dictionary.

        Returns:
            dict[str, Any]: A dictionary representation of the tool, including its name,
              description, and function signature.

        """
        return {
            "name": self._name,
            "description": self._description,
            "function": self.function_signature,
        }


class AbstractDatabaseQueryTool(AbstractTool):
    """
    Abstract base class for tools that query structured data.

    This class provides a common interface for tools that interact with structured data sources.
    """

    def __init__(self, name: str, description: str, default_query_string: str):
        async def query(query_string: str) -> Citation:
            return await self.query(query_string)

        super().__init__(name, description, query)
        self.default_query_string = default_query_string

    @abstractmethod
    async def query(self, query_string: str) -> Citation:
        """
        Execute a query on the structured data source.

        Args:
            query_string (str): The query string to execute if not using the default query string.

        Returns:
            Citation: A Citation object containing the query results.

        """
        pass


class AbstractAoaiChatCompletionTool(AbstractTool):
    """
    Abstract base class for tools that use Azure OpenAI Chat Completion.
    This class provides a common interface for tools that interact with Azure OpenAI's chat completion API.
    """

    def __init__(self, name: str, description: str):
        async def chat_completion(user_question: str) -> Message:
            return await self.chat_completion(user_question)

        super().__init__(name, description, chat_completion)

    @abstractmethod
    async def chat_completion(self, user_question: str) -> Message:
        """
        Perform a chat completion operation.

        Args:
            user_question (str): The input user question for the chat model.

        Returns:
            Message: A Message object containing the response from the chat model.

        """
        pass


class AbstractDocumentSearchTool(AbstractTool):
    """
    Abstract base class for tools that search document sources.

    This class provides a common interface for tools that search document sources.
    """

    def __init__(self, name: str, description: str):
        async def search(query: str, parameters: Optional[dict[str, Any]] = None) -> list[Citation]:
            return await self.search(query, parameters)

        super().__init__(name, description, search)

    @abstractmethod
    async def search(self, query: str, parameters: Optional[dict[str, Any]] = None) -> list[Citation]:
        """
        Search for documents based on the query.

        Args:
            query (str): The search query.
            parameters (Optional[dict[str, Any]]): Optional parameters for the search.

        Returns:
            list[Citation]: A list of Citation objects containing the search results.

        """
        pass


class AbstractStorageAccountTool(AbstractTool):
    """
    Abstract base class for tools that retrieve files from storage account.

    This class provides a common interface for tools that interact with storage accounts.
    """

    def __init__(self, name: str, description: str):
        async def retrieve(file_requests: list[FileRequest]) -> ResponseWithAttachments:
            return await self.retrieve(file_requests)

        super().__init__(name, description, retrieve)

    @abstractmethod
    async def retrieve(self, file_requests: list[FileRequest]) -> ResponseWithAttachments:
        """
        Generate downloadable links for files in the storage account.

        Args:
            file_requests (list[FileRequest]): A list of FileRequest objects containing
                the path and description of the file.

        Returns:
            ResponseWithAttachments: A ResponseWithAttachments object containing the downloadable link and metadata.

        """
        pass
