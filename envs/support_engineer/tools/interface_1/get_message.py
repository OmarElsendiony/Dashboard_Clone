import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetMessage(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_id: str,
        sent_at: str,
        thread_id: Optional[str] = None,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })

        if not channel_id:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'channel_id' is required."
            })

        if not sent_at:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'sent_at' is required."
            })

        channels = data.get("channels", {})
        channel_messages = data.get("channel_messages", {})

        if str(channel_id) not in channels:
            return json.dumps({
                "success": False,
                "error": f"Foreign Key Error: channel_id '{channel_id}' not found."
            })

        found_message = None

        for msg in channel_messages.values():
            if not isinstance(msg, dict):
                continue
            if str(msg.get("channel_id")) != str(channel_id):
                continue
            if str(msg.get("sent_at")) != str(sent_at):
                continue
            if thread_id is not None and str(msg.get("thread_id")) != str(thread_id):
                continue
            found_message = msg
            break

        if found_message is None:
            return json.dumps({
                "success": False,
                "error": (
                    f"Not Found Error: No message found in channel '{channel_id}' "
                    f"with timestamp '{sent_at}'."
                )
            })

        return json.dumps({
            "success": True,
            "message": found_message,
            "message_text": "Message retrieved successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_message",
                "description": (
                    "Retrieves a single Slack message from a specific channel at a precise timestamp. "
                    "Use this function when the exact content of a Slack message is required for "
                    "incident investigation, ticket analysis, auditing, or historical conversation lookup."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "Slack channel identifier."
                        },
                        "sent_at": {
                            "type": "string",
                            "description": "Exact timestamp when the Slack message was sent."
                        },
                        "thread_id": {
                            "type": "string",
                            "description": "Slack thread identifier (optional )."
                        }
                    },
                    "required": ["channel_id", "sent_at"]
                }
            }
        }
