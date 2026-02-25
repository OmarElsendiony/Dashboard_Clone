import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class SendMessageInChannel(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_id: str,
        sender_id: str,
        message_body: str,
        thread_name: str,
    ) -> str:
        timestamp = "2026-02-11T23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            """Generate a new unique ID for a record."""
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        for param_name, param_value in [
            ("channel_id", channel_id),
            ("sender_id", sender_id),
            ("message_body", message_body),
            ("thread_name", thread_name),
        ]:
            if not param_value or not str(param_value).strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Missing required parameter: '{param_name}'",
                    }
                )

        channel_id_str = str(channel_id).strip()
        sender_id_str = str(sender_id).strip()
        message_body_str = str(message_body).strip()
        thread_name_str = str(thread_name).strip()

        channels_dict = data.get("channels", {})
        users_dict = data.get("users", {})
        threads_dict = data.get("threads", {})
        messages_dict = data.get("messages", {})

        if channel_id_str not in channels_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Channel with ID '{channel_id_str}' not found",
                }
            )

        channel = channels_dict[channel_id_str]
        if not isinstance(channel, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Invalid channel data structure for ID '{channel_id_str}'"
                    ),
                }
            )

        channel_status = str(channel.get("status", "")).strip().lower()
        if channel_status != "active":
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Channel '{channel_id_str}' is not active (status: '{channel_status}'). "
                        "Messages can only be sent to active channels."
                    ),
                }
            )

        if sender_id_str not in users_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Sender user with ID '{sender_id_str}' not found",
                }
            )

        sender = users_dict[sender_id_str]
        if not isinstance(sender, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Invalid user data structure for sender ID '{sender_id_str}'"
                    ),
                }
            )

        sender_status = str(sender.get("status", "")).strip().lower()
        if sender_status != "active":
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Sender user '{sender_id_str}' is not active "
                        f"(status: '{sender_status}')"
                    ),
                }
            )

        existing_thread_id = None
        for t_id, t_data in threads_dict.items():
            if not isinstance(t_data, dict):
                continue
            if (
                str(t_data.get("channel_id", "")).strip() == channel_id_str
                and str(t_data.get("thread_name", "")).strip().lower()
                == thread_name_str.lower()
            ):
                thread_status = str(t_data.get("status", "")).strip().lower()
                if thread_status == "active":
                    existing_thread_id = t_id
                    break

        thread_id_str = existing_thread_id
        thread_created = False

        if thread_id_str is None:
            new_thread_id = generate_id(threads_dict)
            new_thread = {
                "thread_id": str(new_thread_id),
                "channel_id": str(channel_id_str),
                "parent_message_id": None,  # Will be set to the first message ID
                "thread_name": str(thread_name_str),
                "status": "active",
                "created_at": timestamp,
            }
            threads_dict[new_thread_id] = new_thread
            thread_id_str = new_thread_id
            thread_created = True

        new_message_id = generate_id(messages_dict)

        new_message = {
            "message_id": str(new_message_id),
            "channel_id": str(channel_id_str),
            "thread_id": str(thread_id_str),
            "sender_id": str(sender_id_str),
            "message_body": str(message_body_str),
            "sent_at": timestamp,
        }

        messages_dict[new_message_id] = new_message

        if thread_created:
            threads_dict[thread_id_str]["parent_message_id"] = str(new_message_id)

        response_data = {
            "success": True,
            "message": new_message,
            "thread_id": str(thread_id_str),
        }

        if thread_created:
            response_data["message_summary"] = (
                f"New thread '{thread_name_str}' created in channel '{channel_id_str}' "
                f"and message sent successfully (message_id: {new_message_id})"
            )
        else:
            response_data["message_summary"] = (
                f"Message sent successfully to existing thread '{thread_name_str}' "
                f"in channel '{channel_id_str}' (message_id: {new_message_id})"
            )

        return json.dumps(response_data)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "send_message_in_channel",
                "description": (
                    "Sends a message to a specific thread within a communication channel. "
                    "If the named thread does not exist in the channel, a new thread is "
                    "automatically created and the message becomes the thread's parent message. "
                    "If the thread already exists, the message is appended to it. "
                    "Use this for project announcements, status updates, blocker escalations, "
                    "incident notifications, engineering progress reports, and all structured "
                    "team communication tied to specific conversation topics."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "The unique identifier of the channel to send the message to. ",
                        },
                        "sender_id": {
                            "type": "string",
                            "description": "The user_id of the user sending the message. ",
                        },
                        "message_body": {
                            "type": "string",
                            "description": "The content of the message to send. ",
                        },
                        "thread_name": {
                            "type": "string",
                            "description": "The name of the thread within the channel. ",
                        },
                    },
                    "required": [
                        "channel_id",
                        "sender_id",
                        "message_body",
                        "thread_name",
                    ],
                },
            },
        }
