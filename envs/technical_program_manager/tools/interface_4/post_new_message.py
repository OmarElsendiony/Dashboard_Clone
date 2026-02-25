import json
from typing import Any, Dict

from tau_bench.envs.tool import Tool


class PostNewMessage(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_id: str,
        sender_id: str,
        message_body: str,
    ) -> str:
        timestamp = "2026-02-11T23:59:00"

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not all([channel_id, sender_id, message_body]):
            return json.dumps(
                {
                    "success": False,
                    "error": "Post requires: channel_id, sender_id, message_body",
                }
            )

        cid = str(channel_id).strip()
        sid = str(sender_id).strip()
        body_str = str(message_body).strip()

        channels = data.get("channels", {})
        users = data.get("users", {})
        messages = data.get("messages", {})

        channel = channels.get(cid)
        if channel is None:
            return json.dumps(
                {"success": False, "error": f"Channel '{cid}' not found"}
            )
        if str(channel.get("status", "")) != "active":
            return json.dumps(
                {
                    "success": False,
                    "error": f"Channel '{cid}' is not active. Current status: {str(channel.get('status', ''))}",
                }
            )

        user = users.get(sid)
        if user is None:
            return json.dumps(
                {"success": False, "error": f"User '{sid}' not found"}
            )
        if str(user.get("status", "")) != "active":
            return json.dumps(
                {
                    "success": False,
                    "error": f"User '{sid}' is not active. Current status: {str(user.get('status', ''))}",
                }
            )

        if messages:
            max_id = max(int(k) for k in messages.keys())
            new_id = str(max_id + 1)
        else:
            new_id = "1"

        new_message = {
            "message_id": new_id,
            "channel_id": cid,
            "sender_id": sid,
            "message_body": body_str,
            "sent_at": timestamp,
        }

        messages[new_id] = new_message

        response = {
            "message_id": str(new_message.get("message_id", "")),
            "channel_id": str(new_message.get("channel_id", "")),
            "sender_id": str(new_message.get("sender_id", "")),
            "message_body": str(new_message.get("message_body", "")),
            "sent_at": str(new_message.get("sent_at", "")),
        }
        return json.dumps({"success": True, "message": response})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "post_new_message",
                "description": "Posts a new message to a communication channel.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "Unique channel identifier.",
                        },
                        "sender_id": {
                            "type": "string",
                            "description": "Sender user identifier.",
                        },
                        "message_body": {
                            "type": "string",
                            "description": "Message body text",
                        },
                    },
                    "required": ["channel_id", "sender_id", "message_body"],
                },
            },
        }
