import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateThread(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_id: str,
        thread_name: str,
        description: Optional[str] = None,
    ) -> str:
        timestamp = "2026-02-02 23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            """Generate a new unique ID for a record."""
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        def thread_name_exists(threads_dict: Dict[str, Any], channel_id_str: str, thread_name_str: str) -> bool:
            """Check if a thread with the same name already exists in the channel."""
            for thread in threads_dict.values():
                if not isinstance(thread, dict):
                    continue
                if (str(thread.get("channel_id", "")).strip() == channel_id_str and
                    str(thread.get("thread_name", "")).strip() == thread_name_str):
                    return True
            return False

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        if not channel_id:
            return json.dumps({"success": False, "error": "Missing required parameter: 'channel_id'"})

        if not thread_name:
            return json.dumps({"success": False, "error": "Missing required parameter: 'thread_name'"})

        threads_dict = data.get("threads", {})
        channels_dict = data.get("channels", {})

        channel_id_str = str(channel_id).strip()
        thread_name_str = str(thread_name).strip()
        description_str = str(description).strip() if description else None

        if not thread_name_str:
            return json.dumps({
                "success": False,
                "error": "Thread name cannot be empty"
            })

        if channel_id_str not in channels_dict:
            return json.dumps({
                "success": False,
                "error": f"Channel with ID '{channel_id_str}' not found"
            })

        channel = channels_dict[channel_id_str]

        if not isinstance(channel, dict):
            return json.dumps({
                "success": False,
                "error": f"Invalid channel data structure for channel ID '{channel_id_str}'"
            })

        # Validate channel status - can only create threads in active channels
        channel_status = str(channel.get("status", "")).strip()
        if channel_status != "active":
            return json.dumps({
                "success": False,
                "error": f"Cannot create thread in channel '{channel_id_str}' with status '{channel_status}'. Channel must be active."
            })

        if thread_name_exists(threads_dict, channel_id_str, thread_name_str):
            return json.dumps({
                "success": False,
                "error": f"Thread with name '{thread_name_str}' already exists in channel '{channel_id_str}'"
            })

        # Validate thread naming convention (based on policy requirements)
        # Expected format: [prefix]-[ticket_num]-[date]
        # Allowed prefixes: incident-, investigation-
        thread_name_parts = thread_name_str.split("-")

        # Check if thread name follows naming convention (at least 3 parts)
        if len(thread_name_parts) >= 3:
            prefix = thread_name_parts[0].lower()
            valid_prefixes = ["incident", "investigation"]

            # If it appears to follow the convention, validate strictly
            if prefix in valid_prefixes:
                # Validate format: prefix-ticket_num-date
                if len(thread_name_parts) < 3:
                    return json.dumps({
                        "success": False,
                        "error": f"Thread name '{thread_name_str}' does not follow required format: [prefix]-[ticket_num]-[date]. Example: 'incident-TKT-001234-2026-01-30'"
                    })
            else:
                # If prefix is not recognized but format looks like convention, warn about prefix
                potential_prefix = thread_name_parts[0]
                if potential_prefix not in valid_prefixes and len(thread_name_parts) >= 3:
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid thread name prefix '{potential_prefix}'. Allowed prefixes: {', '.join(valid_prefixes)}. Expected format: [prefix]-[ticket_num]-[date]"
                    })

        # Generate thread ID
        new_thread_id = generate_id(threads_dict)

        # Create new thread
        new_thread = {
            "thread_id": str(new_thread_id) if new_thread_id else None,
            "channel_id": str(channel_id_str) if channel_id_str else None,
            "thread_name": str(thread_name_str) if thread_name_str else None,
            "description": str(description_str) if description_str else None,
            "status": "active",
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        # Add thread to dictionary
        threads_dict[new_thread_id] = new_thread

        # Prepare return data
        thread_return = new_thread.copy()
        thread_return["channel_name"] = str(channel.get("name")) if channel.get("name") else None
        thread_return["channel_type"] = str(channel.get("channel_type")) if channel.get("channel_type") else None

        # Build success message
        message = f"Thread '{thread_name_str}' created successfully in channel '{channel.get('name', channel_id_str)}'"

        return json.dumps({
            "success": True,
            "thread": thread_return,
            "message": message,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return tool metadata for the create_thread function."""
        return {
            "type": "function",
            "function": {
                "name": "create_thread",
                "description": (
                    "Creates a new conversation thread within a communication channel. "
                    "This function establishes a focused discussion space for specific topics or incidents. "
                    "Use this to organize incident-related communications, create investigation workspaces, "
                    "establish coordination threads for P0/P1 incidents, or separate different topics within a channel. "
                    "Thread names should follow naming conventions with appropriate prefixes for incident or investigation threads."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "The unique identifier of the channel where the thread will be created.",
                        },
                        "thread_name": {
                            "type": "string",
                            "description": "The name of the thread. Should follow naming convention: [prefix]-[ticket_num]-[date] where prefix is 'incident' or 'investigation'.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional. A description of the thread's purpose or topic.",
                        },
                    },
                    "required": ["channel_id", "thread_name"],
                },
            },
        }
