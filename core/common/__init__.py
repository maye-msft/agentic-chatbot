from datetime import datetime
from enum import Enum
from typing import Any, Union

from pydantic import BaseModel


class Citation(BaseModel):
    """
    An item retrieved from a knowledge source.

    Attributes:
        item_id (str): Unique identifier for the item
        source (str): Source identifier (e.g., database name, document store name)
        metadata (dict[str, Any]): Additional item information

    """

    item_id: str
    source: str
    metadata: dict[str, Any]


class CitationSourceType(Enum):
    """Represents the type of source for a citation."""

    DOCUMENT = "document"
    DATABASE = "database"


class UserProfile(BaseModel):
    """
    Information about the current authenticated user.

    Attributes:
        user_id (str): Unique identifier for the user
        display_name (str): User's display name
        email (str): User's email address
        metadata (dict[str, Any]): Additional user information

    """

    user_id: str
    display_name: str
    email: str
    metadata: dict[str, Any]


class MediaType(Enum):
    """Represents the type of media."""

    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"


class MediaAttachment(BaseModel):
    """Represents an attachment of media."""

    type: MediaType  # "image", "audio", "video", "file"
    content: str  # URL or base64 encoded string
    data_description: str  # Description of the attachment
    start_time: str  # Start time for audio/video
    autoplay: bool  # Autoplay for audio/video
    loop: bool  # Loop for audio/video


class GraphType(Enum):
    """Represents the type of a graph."""

    BAR = "bar"
    PIE = "pie"
    LINE = "line"
    STACKED_BAR = "stacked_bar"


class GraphAttachment(BaseModel):
    """Represents an attachment of a graph."""

    type: GraphType
    data_description: str
    dataset_json: str  # JSON string
    x: str
    y: list[str]


class ResponseWithAttachments(BaseModel):
    """Represents a response that includes attachments."""

    text: str
    attachments: list[Union[MediaAttachment, GraphAttachment]]


class FileRequest(BaseModel):
    """
    Represents a file request.

    Attributes:
        path (str): Path to the file in the storage account
        description (str): Description of the file

    """

    path: str
    description: str


class Message(BaseModel):
    """
    Represents a single message in a conversation.

    Attributes:
        message_id (str): Unique identifier for the message
        role (str): The role of the message sender (e.g., "user", "assistant")
        content (str): The text content of the message
        created_at (datetime): When the message was created
        citations (list[Citation]): List of citations referenced in the message
        metadata (dict[str, Any]): Additional information about the message
        attachments (list[Union[MediaAttachment, GraphAttachment]]): List of attachments (e.g., images, files)

    """

    message_id: str
    role: str
    content: str
    created_at: datetime
    citations: list[Citation]
    metadata: dict[str, Any]
    attachments: list[Union[MediaAttachment, GraphAttachment]]
