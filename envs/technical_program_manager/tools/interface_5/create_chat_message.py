import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateChatMessage(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_id: str,
        sender_id: str,
        message_body: str,
        thread_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format for messages"}
            )

        if channel_id is None:
            return json.dumps({"success": False, "error": "channel_id is required"})

        if sender_id is None:
            return json.dumps({"success": False, "error": "sender_id is required"})

        if not message_body:
            return json.dumps({"success": False, "error": "message_body is required"})

        channels = data.get("channels", {})
        channel = None
        channel_key_str = str(channel_id)

        if channel_key_str in channels:
            channel_data = channels[channel_key_str]
            if str(channel_data.get("channel_id")) == str(channel_id):
                channel = channel_data

        if not channel:
            for channel_data in channels.values():
                if str(channel_data.get("channel_id")) == str(channel_id):
                    channel = channel_data
                    break

        if not channel:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Channel with ID {str(channel_id)} not found",
                }
            )

        users = data.get("users", {})
        sender_exists = False

        for _user_key, user_data in users.items():
            if str(user_data.get("user_id")) == str(sender_id):
                sender_exists = True
                break

        if not sender_exists:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with ID {str(sender_id)} not found in users table",
                }
            )

        if thread_id is not None:
            threads = data.get("threads", {})
            thread_exists = False

            for _thread_key, thread_data in threads.items():
                if str(thread_data.get("thread_id")) == str(thread_id):
                    thread_exists = True
                    break

            if not thread_exists:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Thread with ID {str(thread_id)} not found",
                    }
                )

        # Generate message_id
        def generate_id(table: Dict[str, Any]) -> int:
            if not table:
                return 1
            return max(int(k) for k in table.keys()) + 1

        messages = data.setdefault("messages", {})
        message_id = generate_id(messages)
        timestamp = "2026-02-11T23:59:00"

        new_message = {
            "message_id": str(message_id),
            "channel_id": str(channel_id),
            "thread_id": str(thread_id) if thread_id is not None else None,
            "sender_id": str(sender_id),
            "message_body": str(message_body),
            "sent_at": str(timestamp),
        }

        messages[str(message_id)] = new_message

        return json.dumps(
            {
                "success": True,
                "message": new_message,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_chat_message",
                "description": "Create a new chat message in a channel. Use this to send messages to project channels, either as a new message or as a reply in an existing thread.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "The channel ID where the message will be sent",
                        },
                        "sender_id": {
                            "type": "string",
                            "description": "The user ID of the person sending the message",
                        },
                        "message_body": {
                            "type": "string",
                            "description": "The content of the message",
                        },
                        "thread_id": {
                            "type": "string",
                            "description": "Optional thread ID to reply to an existing thread",
                        },
                    },
                    "required": ["channel_id", "sender_id", "message_body"],
                },
            },
        }
