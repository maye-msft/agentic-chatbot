"""Streamlit app for demonstrating the Conversation Service with multiple agents and users."""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any, Awaitable, Dict, List, Optional

import streamlit as st

from core.conversation_service import ConversationService
from core.examples.math_llama_index_agent import MathLlamaIndexAgent
from core.examples.math_semantic_kernel_agent import MathSemanticKernelAgent
from core.persistence.json_file_persistence_strategy import (
    JsonFilePersistenceStrategy,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)

# Predefined users
PREDEFINED_USERS = {
    "user1": "94a7b21c-d243-4bdf-8a11-1f144e42f17a",
    "user2": "6ef12c89-7532-4a9d-bb15-7e98f321c453",
    "user3": "fb2ab730-9ac5-48f5-90d9-ad42fe5414a0",
}


class StreamlitConversationApp:
    """
    A class-based Streamlit application for managing conversations with multiple agents.

    This app handles user management, conversation lifecycle, and message exchanges
    with configurable persistence strategies and agents.

    Args:
        persistence_strategy (Optional[Any]): The persistence strategy for storing conversations.
                             Defaults to JsonFilePersistenceStrategy if None.
        agents (Optional[Dict[str, Any]]): Dictionary of available agents. Defaults to built-in agents if None.
        title (str): The title to display in the Streamlit app.
              Defaults to "Conversation Service Streamlit Demo".

    """

    def __init__(
        self,
        persistence_strategy: Optional[Any] = None,
        agents: Optional[Dict[str, Any]] = None,
        title: str = "Conversation Service Streamlit Demo",
    ) -> None:
        # Set default persistence strategy
        if persistence_strategy is None:
            persistence_strategy = JsonFilePersistenceStrategy()

        # Set default agents
        if agents is None:
            agents = {
                "math_semantic_kernel_agent": MathSemanticKernelAgent(),
                "math_llama_index_agent": MathLlamaIndexAgent(),
            }

        # Initialize the conversation service with provided configuration
        self.service = ConversationService(persistence_strategy=persistence_strategy, agents=agents)
        self.title = title
        self._setup_session_state()

    def _setup_session_state(self) -> None:
        """Initialize session state for the Streamlit app."""
        if "user_id" not in st.session_state:
            st.session_state.user_id = PREDEFINED_USERS["user1"]
        if "service" not in st.session_state:
            st.session_state.service = self.service
        if "available_agents" not in st.session_state:
            st.session_state.available_agents = self.service.get_available_agents()
        if "active_conversation_id" not in st.session_state:
            st.session_state.active_conversation_id = None
        if "conversations" not in st.session_state:
            st.session_state.conversations = []
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "show_tool_usage" not in st.session_state:
            st.session_state.show_tool_usage = True
        if "error" not in st.session_state:
            st.session_state.error = None
        if "status_message" not in st.session_state:
            st.session_state.status_message = None
        if "status_message_time" not in st.session_state:
            st.session_state.status_message_time = None
        if "need_refresh" not in st.session_state:
            st.session_state.need_refresh = False

    def get_available_agents(self) -> Dict[str, Any]:
        """
        Retrieve available agents from the ConversationService.

        Returns:
            Dict[str, Any]: Dictionary of available agents.

        """
        return self.service.get_available_agents()

    @staticmethod
    def format_messages(messages: List[Any]) -> List[Dict[str, Any]]:
        """
        Format a list of message objects into dictionaries for display.

        Args:
            messages (List[Any]): List of message objects.

        Returns:
            List[Dict[str, Any]]: List of formatted message dictionaries.

        """
        formatted = []
        for msg in messages:
            if hasattr(msg, "role") and hasattr(msg, "content"):
                tool_usage = None
                if hasattr(msg, "metadata") and msg.metadata:
                    if isinstance(msg.metadata, dict) and "tool_usage" in msg.metadata:
                        tool_usage = msg.metadata["tool_usage"]
                        tool_count = len(tool_usage) if tool_usage else 0
                        logger.info(f"Extracted tool_usage from message {msg.role}: {tool_count} tools")
                    else:
                        logger.debug(f"Message {msg.role} has metadata but no tool_usage or wrong type")
                else:
                    logger.debug(f"Message {msg.role} has no metadata")
                formatted_msg = {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": getattr(msg, "timestamp", time.time()),
                    "tool_usage": tool_usage,
                }
                formatted.append(formatted_msg)
        return formatted

    @staticmethod
    def display_message(message: Dict[str, Any], show_tool_usage: bool = True) -> None:
        """
        Display a single message in the Streamlit app.

        Args:
            message (Dict[str, Any]): The message to display.
            show_tool_usage (bool): Whether to show tool usage details.

        """
        role = message.get("role", "unknown")
        content = message.get("content", "")
        tool_usage = message.get("tool_usage")

        # Debug logging
        if role in ("agent", "assistant"):
            has_tool = tool_usage is not None
            logger.info(f"Displaying agent message: has_tool_usage={has_tool}, show_tool_usage={show_tool_usage}")
            if tool_usage:
                count = len(tool_usage) if isinstance(tool_usage, list) else "not a list"
                logger.info(f"Tool usage present: {count}")

        if role == "user":
            st.markdown(f"**👤 You:** {content}")
        else:
            st.markdown(f"**🤖 Agent:** {content}")
        # Check for both "agent" and "assistant" roles since both are used
        if show_tool_usage and role in ("agent", "assistant") and tool_usage:
            with st.expander("Tool Usage Details"):
                if isinstance(tool_usage, str):
                    try:
                        tool_usage = json.loads(tool_usage)
                    except Exception:
                        pass
                st.json(tool_usage)

    @staticmethod
    def run_async(coro: Awaitable[Any]) -> Any:
        """
        Run an async coroutine in Streamlit, handling event loop issues.

        Args:
            coro (Awaitable[Any]): The coroutine to run.

        Returns:
            Any: The result of the coroutine.

        Raises:
            Exception: If the coroutine cannot be run.

        """
        try:
            return asyncio.run(coro)
        except RuntimeError:
            try:
                import nest_asyncio

                nest_asyncio.apply()
                return asyncio.get_event_loop().run_until_complete(coro)
            except Exception as e:
                logger.error(f"Error in run_async: {e}")
                raise

    def set_status_message(self, msg: str) -> None:
        """
        Set a status message and its timestamp in session state.

        Args:
            msg (str): The status message to set.

        """
        st.session_state.status_message = msg
        st.session_state.status_message_time = time.time()

    def load_conversation_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Load messages for a given conversation.

        Args:
            conversation_id (str): The ID of the conversation.

        Returns:
            List[Dict[str, Any]]: List of formatted messages.

        """
        try:
            logger.info(f"Loading conversation messages for: {conversation_id}")
            conversation = self.run_async(
                self.service.load_conversation(conversation_id=conversation_id, user_id=st.session_state.user_id)
            )
            if conversation and hasattr(conversation, "messages"):
                formatted = self.format_messages(conversation.messages)
                logger.info(f"Loaded and formatted {len(formatted)} messages")
                return formatted
            else:
                logger.warning(f"No conversation found or no messages attribute for {conversation_id}")
        except Exception as e:
            logger.error(f"Error loading conversation {conversation_id}: {e}")
            st.session_state.error = f"Error loading conversation: {str(e)}"
        return []

    def refresh_conversations(self) -> None:
        """Refresh the list of conversations for the current user."""
        st.session_state.error = None
        try:
            conversations = self.run_async(self.service.list_conversations(user_id=st.session_state.user_id))
            if conversations and isinstance(conversations, dict) and "items" in conversations:
                st.session_state.conversations = conversations["items"]  # type: ignore[index]
                # Ensure active_conversation_id is set if only one conversation exists
                if len(st.session_state.conversations) == 1:
                    st.session_state.active_conversation_id = st.session_state.conversations[0]["conversation_id"]
                elif not any(
                    conv.get("conversation_id") == st.session_state.active_conversation_id
                    for conv in st.session_state.conversations
                ):
                    # If the current active_conversation_id is not in the refreshed list, reset it
                    st.session_state.active_conversation_id = None
                self.set_status_message("Conversations refreshed successfully.")
                st.session_state.need_refresh = False
        except Exception as e:
            logger.error(f"Error refreshing conversations: {e}")
            st.session_state.error = f"Error refreshing conversations: {str(e)}"

    def run(self) -> None:
        """Run the Streamlit app."""
        # Configure page
        st.set_page_config(page_title="Conversation Service Demo", layout="wide")
        st.title(self.title)

        # Refresh conversations if needed
        if st.session_state.need_refresh or not st.session_state.conversations:
            self.refresh_conversations()
            # After refresh, if there is an active conversation, load its messages
            if st.session_state.active_conversation_id:
                st.session_state.messages = self.load_conversation_messages(st.session_state.active_conversation_id)
            elif st.session_state.conversations:
                # If no active conversation, but there are conversations, set the first as active and load its messages
                st.session_state.active_conversation_id = st.session_state.conversations[0]["conversation_id"]
                st.session_state.messages = self.load_conversation_messages(st.session_state.active_conversation_id)

        # IMPORTANT: Ensure messages are loaded if we have an active conversation but no messages
        if st.session_state.active_conversation_id and not st.session_state.messages:
            logger.info(
                f"Page refresh detected: Loading messages for conversation {st.session_state.active_conversation_id}"
            )
            st.session_state.messages = self.load_conversation_messages(st.session_state.active_conversation_id)

        # Render the UI
        self._render_sidebar()
        self._render_main_area()

    def _render_sidebar(self) -> None:
        """Render the sidebar with user selection and conversation management."""
        # User selection section
        st.sidebar.header("User")
        current_user_name = next(
            (name for name, uid in PREDEFINED_USERS.items() if uid == st.session_state.user_id), "Unknown"
        )
        st.sidebar.info(f"👤 {current_user_name}")

        if st.sidebar.button(
            "🔄 Switch User", key="switch_user_btn", use_container_width=True, help="Change to a different user"
        ):
            self._select_user_dialog()

        st.sidebar.divider()

        # Conversation management section
        st.sidebar.header("Conversations")

        # Show active conversation title
        if st.session_state.active_conversation_id:
            active_conv = next(
                (
                    c
                    for c in st.session_state.conversations
                    if c.get("conversation_id") == st.session_state.active_conversation_id
                ),
                None,
            )
            if active_conv:
                st.sidebar.info(f"📝 {active_conv.get('title', 'Untitled')}")
            else:
                st.sidebar.info("📝 No conversation selected")
        else:
            st.sidebar.info("📝 No conversation selected")

        # Action buttons
        if st.sidebar.button(
            "💬 Switch Conversation",
            key="switch_conv_btn",
            use_container_width=True,
            help="Choose a different conversation",
        ):
            self._select_conversation_dialog()

        if st.sidebar.button(
            "➕ New Conversation", key="new_conv_btn", use_container_width=True, help="Start a new conversation"
        ):
            self._create_conversation_dialog()

        # Delete and Reset buttons (only show if there's an active conversation)
        if st.session_state.active_conversation_id:
            if st.sidebar.button(
                "🗑️ Delete Conversation",
                key="delete_conv_btn",
                use_container_width=True,
                help="Delete this conversation",
            ):
                self._confirm_delete_dialog()

            if st.sidebar.button(
                "🔃 Reset Conversation", key="reset_conv_btn", use_container_width=True, help="Clear all messages"
            ):
                self._reset_conversation()

        st.sidebar.divider()

        # Display error and status messages
        if st.session_state.error:
            st.error(st.session_state.error)
            st.session_state.error = None

        if st.session_state.status_message:
            st.success(st.session_state.status_message)
            if st.session_state.status_message_time and time.time() - st.session_state.status_message_time > 5:
                st.session_state.status_message = None
                st.session_state.status_message_time = None

    def _render_main_area(self) -> None:
        """Render the main chat area."""
        if st.session_state.active_conversation_id:
            # Display conversation title
            active_conv = next(
                (
                    c
                    for c in st.session_state.conversations
                    if c.get("conversation_id") == st.session_state.active_conversation_id
                ),
                None,
            )
            if active_conv:
                st.subheader(f"Chat: {active_conv.get('title', 'Untitled')}")
            else:
                st.subheader("Chat")

            # Display messages
            for msg in st.session_state.messages:
                self.display_message(msg, st.session_state.show_tool_usage)

            # Message input form
            with st.form("chat_form", clear_on_submit=True):
                user_input = st.text_input("Your message", "")
                submitted = st.form_submit_button("Send")

                if submitted and user_input.strip():
                    self._handle_message_submission(user_input)

        else:
            st.info("Select or create a conversation to start chatting.")

        # Tool usage toggle
        show_tool_usage = st.checkbox(
            "Show Tool Usage Details", value=st.session_state.show_tool_usage, key="tool_usage_toggle"
        )
        if show_tool_usage != st.session_state.show_tool_usage:
            st.session_state.show_tool_usage = show_tool_usage
            st.rerun()

        # Debug panel
        if st.checkbox("🐛 Debug: Show Tool Usage Status"):
            self._render_debug_panel()

    def _handle_message_submission(self, user_input: str) -> None:
        """
        Handle user message submission.

        Args:
            user_input (str): The user's message.

        """
        try:
            # Add user message immediately for better UX
            user_message = {"role": "user", "content": user_input, "timestamp": time.time(), "tool_usage": None}
            st.session_state.messages.append(user_message)

            # Send message and get response
            response = self.run_async(
                self.service.send_message(
                    conversation_id=st.session_state.active_conversation_id,
                    user_id=st.session_state.user_id,
                    message_content=user_input,
                )
            )

            # Extract tool usage if present
            tool_usage = None
            if hasattr(response, "metadata") and response.metadata:
                if isinstance(response.metadata, dict) and "tool_usage" in response.metadata:
                    tool_usage = response.metadata["tool_usage"]

            # Create agent message
            agent_message = {
                "role": "agent",
                "content": getattr(response, "content", ""),
                "timestamp": time.time(),
                "tool_usage": tool_usage,
            }

            # Add agent message to state
            st.session_state.messages.append(agent_message)
            self.set_status_message("Message sent successfully.")

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            st.session_state.error = f"Error sending message: {str(e)}"
            # Reload the conversation to ensure consistency
            try:
                st.session_state.messages = self.load_conversation_messages(st.session_state.active_conversation_id)
            except Exception as reload_error:
                logger.error(f"Error reloading conversation: {reload_error}")

        st.rerun()

    def _render_debug_panel(self) -> None:
        """Render the debug panel for tool usage information."""
        st.write("### Tool Usage Debug Info")
        st.write(f"**Total messages:** {len(st.session_state.messages)}")
        st.write(f"**Show tool usage toggle:** {st.session_state.show_tool_usage}")

        for i, msg in enumerate(st.session_state.messages):
            with st.expander(f"Message {i + 1}: {msg.get('role', 'unknown')}"):
                st.write(f"**Role:** {msg.get('role')}")
                st.write(f"**Has tool_usage:** {msg.get('tool_usage') is not None}")
                if msg.get("tool_usage"):
                    st.write(f"**Tool usage count:** {len(msg['tool_usage'])}")
                    for j, tool in enumerate(msg["tool_usage"]):
                        st.write(f"  - Tool {j + 1}: {tool.get('tool_name', 'unknown')}")
                else:
                    st.write("**Tool usage:** None")
                st.write(f"**Content preview:** {msg.get('content', '')[:100]}...")

    def _select_user_dialog(self) -> None:
        """Show dialog to select a user."""

        @st.dialog("Select User", width="large")
        def dialog() -> None:
            st.write("Choose a user to switch to:")

            # Create table data
            table_data = []
            for user_name, user_id in PREDEFINED_USERS.items():
                is_active = user_id == st.session_state.user_id
                table_data.append(
                    {
                        "User": user_name,
                        "User ID": user_id[:8] + "...",
                        "full_id": user_id,
                        "is_active": is_active,
                        "tooltip": f"User ID: {user_id}\n{'(Currently Active)' if is_active else ''}",
                    }
                )

            current_index = next((i for i, row in enumerate(table_data) if row["is_active"]), 0)

            if "dialog_selected_user" not in st.session_state:
                st.session_state.dialog_selected_user = current_index

            # Table header
            header_cols = st.columns([1, 4, 3])
            with header_cols[0]:
                st.write("**Select**")
            with header_cols[1]:
                st.write("**User**")
            with header_cols[2]:
                st.write("**User ID**")

            st.divider()

            # Display users with checkboxes
            for idx, row in enumerate(table_data):
                cols = st.columns([1, 4, 3])
                with cols[0]:
                    st.checkbox(
                        "",
                        key=f"user_check_{idx}",
                        value=(st.session_state.dialog_selected_user == idx),
                        label_visibility="collapsed",
                        help=row["tooltip"],
                        on_change=lambda i=idx: setattr(st.session_state, "dialog_selected_user", i),
                    )
                with cols[1]:
                    if row["is_active"]:
                        st.write(f"**{row['User']}** (Current)")
                    else:
                        st.write(row["User"])
                with cols[2]:
                    st.write(row["User ID"])

            st.divider()

            if st.button(
                "✓ Confirm",
                key="confirm_user_switch",
                use_container_width=True,
                type="primary",
            ):
                selected_user = table_data[st.session_state.dialog_selected_user]
                if selected_user["full_id"] != st.session_state.user_id:
                    st.session_state.user_id = selected_user["full_id"]
                    st.session_state.active_conversation_id = None
                    st.session_state.conversations = []
                    st.session_state.messages = []
                    st.session_state.error = None
                    st.session_state.status_message = None
                    self.set_status_message(f"Switched to {selected_user['User']}")
                del st.session_state.dialog_selected_user
                st.rerun()

        dialog()

    def _select_conversation_dialog(self) -> None:
        """Show dialog to select a conversation."""

        @st.dialog("Select Conversation", width="large")
        def dialog() -> None:
            if not st.session_state.conversations:
                st.info("No conversations found. Create a new one to get started!")
                return

            st.write("Choose a conversation to switch to:")

            table_data = []
            for conv in st.session_state.conversations:
                title = conv.get("title", "Untitled")
                conv_id = conv.get("conversation_id", "")
                is_active = conv_id == st.session_state.active_conversation_id
                created_at = conv.get("created_at", "")
                last_updated = conv.get("last_updated_at", "")

                # Format dates
                try:
                    if isinstance(created_at, str):
                        created_date = datetime.fromisoformat(created_at).strftime("%Y-%m-%d %H:%M")
                    else:
                        created_date = "N/A"
                except Exception:
                    created_date = "N/A"

                try:
                    if isinstance(last_updated, str):
                        updated_date = datetime.fromisoformat(last_updated).strftime("%Y-%m-%d %H:%M")
                    else:
                        updated_date = "N/A"
                except Exception:
                    updated_date = "N/A"

                tooltip_text = f"{title}\nCreated: {created_date}\nLast Updated: {updated_date}"
                if is_active:
                    tooltip_text += "\n(Currently Active)"

                table_data.append(
                    {
                        "Title": title,
                        "Created": created_date,
                        "Updated": updated_date,
                        "conversation_id": conv_id,
                        "is_active": is_active,
                        "tooltip": tooltip_text,
                    }
                )

            current_index = next((i for i, row in enumerate(table_data) if row["is_active"]), 0)

            if "dialog_selected_conv" not in st.session_state:
                st.session_state.dialog_selected_conv = current_index

            header_cols = st.columns([1, 5, 2, 2])
            with header_cols[0]:
                st.write("**Select**")
            with header_cols[1]:
                st.write("**Title**")
            with header_cols[2]:
                st.write("**Created**")
            with header_cols[3]:
                st.write("**Updated**")

            st.divider()

            with st.container(height=400):
                for idx, row in enumerate(table_data):
                    cols = st.columns([1, 5, 2, 2])
                    with cols[0]:
                        st.checkbox(
                            "",
                            key=f"conv_check_{idx}",
                            value=(st.session_state.dialog_selected_conv == idx),
                            label_visibility="collapsed",
                            help=row["tooltip"],
                            on_change=lambda i=idx: setattr(st.session_state, "dialog_selected_conv", i),
                        )
                    with cols[1]:
                        if row["is_active"]:
                            st.write(f"**{row['Title']}** (Current)")
                        else:
                            st.write(row["Title"])
                    with cols[2]:
                        st.write(row["Created"])
                    with cols[3]:
                        st.write(row["Updated"])

            st.divider()

            if st.button(
                "✓ Confirm",
                key="confirm_conversation_switch",
                use_container_width=True,
                type="primary",
            ):
                selected_row = table_data[st.session_state.dialog_selected_conv]
                st.session_state.active_conversation_id = selected_row["conversation_id"]
                st.session_state.messages = self.load_conversation_messages(selected_row["conversation_id"])
                del st.session_state.dialog_selected_conv
                st.rerun()

        dialog()

    def _create_conversation_dialog(self) -> None:
        """Show dialog to create a new conversation."""

        @st.dialog("Create New Conversation", width="large")
        def dialog() -> None:
            st.write("Select an agent to start a new conversation:")

            agent_names = [info["name"] for info in st.session_state.available_agents.values()]
            agent_ids = list(st.session_state.available_agents.keys())

            for i, (agent_id, agent_name) in enumerate(zip(agent_ids, agent_names, strict=True)):
                agent_info = st.session_state.available_agents[agent_id]
                description = agent_info.get("description", "No description available")

                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{agent_name}**")
                        st.caption(description)
                    with col2:
                        if st.button("Select", key=f"select_agent_{i}", use_container_width=True):
                            try:
                                conversation_title = (
                                    f"{agent_name} - Conversation {len(st.session_state.conversations) + 1}"
                                )
                                conversation = self.run_async(
                                    self.service.create_conversation(
                                        agent=agent_info["instance"],
                                        user_id=st.session_state.user_id,
                                        title=conversation_title,
                                    )
                                )

                                if conversation:
                                    st.session_state.active_conversation_id = getattr(
                                        conversation, "conversation_id", None
                                    )
                                    st.session_state.messages = []
                                    self.set_status_message(f"Created new conversation: {conversation_title}")
                                    st.session_state.need_refresh = True
                                    st.rerun()
                            except Exception as e:
                                logger.error(f"Error creating conversation: {e}")
                                st.error(f"Error creating conversation: {str(e)}")

        dialog()

    def _confirm_delete_dialog(self) -> None:
        """Show confirmation dialog before deleting conversation."""

        @st.dialog("Confirm Delete", width="large")
        def dialog() -> None:
            active_conv = next(
                (
                    c
                    for c in st.session_state.conversations
                    if c.get("conversation_id") == st.session_state.active_conversation_id
                ),
                None,
            )

            if active_conv:
                st.warning("⚠️ Are you sure you want to delete this conversation?")
                st.write(f"**{active_conv.get('title', 'Untitled')}**")
                st.write("")
                st.write("This action cannot be undone. All messages in this conversation will be permanently deleted.")
                st.write("")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("❌ Cancel", key="cancel_delete", use_container_width=True):
                        st.rerun()
                with col2:
                    if st.button("🗑️ Delete", key="confirm_delete", use_container_width=True, type="primary"):
                        self._delete_conversation_confirmed()

        dialog()

    def _delete_conversation_confirmed(self) -> None:
        """Delete the currently active conversation (after confirmation)."""
        if st.session_state.active_conversation_id:
            try:
                self.run_async(
                    self.service.delete_conversation(
                        conversation_id=st.session_state.active_conversation_id, user_id=st.session_state.user_id
                    )
                )

                st.session_state.active_conversation_id = None
                st.session_state.messages = []
                self.set_status_message("Conversation deleted successfully.")
                st.session_state.need_refresh = True
                st.session_state.conversations = []
                st.rerun()
            except Exception as e:
                st.error(f"Failed to delete conversation: {e}")

    def _reset_conversation(self) -> None:
        """Reset the currently active conversation, clearing its messages."""
        if st.session_state.active_conversation_id:
            try:
                self.run_async(
                    self.service.reset_conversation(
                        conversation_id=st.session_state.active_conversation_id, user_id=st.session_state.user_id
                    )
                )
                st.session_state.messages = []
                st.success("Conversation reset.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to reset conversation: {e}")


def main() -> None:
    """Main entry point for the Streamlit app."""
    # Create app instance with default persistence strategy and agents
    app = StreamlitConversationApp()
    # Run the app
    app.run()


if __name__ == "__main__":
    main()
