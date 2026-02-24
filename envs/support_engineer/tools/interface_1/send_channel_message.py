import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class SendChannelMessage(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_id: str,
        sender_id: str,
        message: str,
        thread_id: Optional[str] = None,
        related_ticket_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not channel_id:
            return json.dumps({"success": False, "error": "Missing required argument: 'channel_id' is required."})

        if not sender_id:
            return json.dumps({"success": False, "error": "Missing required argument: 'sender_id' is required."})

        if not message:
            return json.dumps({"success": False, "error": "Missing required argument: 'message' is required."})

        channel_id = str(channel_id).strip()
        sender_id = str(sender_id).strip()
        message = str(message)

        channels = data.get("channels", {})
        users = data.get("users", {})
        channel_messages = data.get("channel_messages", {})

        if channel_id not in channels:
            return json.dumps({"success": False, "error": f"Not Found Error: channel_id '{channel_id}' not found."})

        if sender_id not in users:
            return json.dumps({"success": False, "error": f"Not Found Error: sender_id '{sender_id}' not found."})

        max_id = 0
        for k in channel_messages.keys():
            try:
                num = int(str(k))
                if num > max_id:
                    max_id = num
            except ValueError:
                continue

        for v in channel_messages.values():
            if isinstance(v, dict):
                try:
                    num = int(str(v.get("message_id", "0")))
                    if num > max_id:
                        max_id = num
                except ValueError:
                    continue

        new_message_id = str(max_id + 1)
        timestamp = "2026-02-02 23:59:00"

        new_message = {
            "message_id": new_message_id,
            "channel_id": channel_id,
            "thread_id": str(thread_id).strip() if thread_id else "",
            "sender_id": sender_id,
            "message": message,
            "related_ticket_id": str(related_ticket_id).strip() if related_ticket_id else "",
            "sent_at": timestamp,
            "created_at": timestamp,
            "updated_at": timestamp
        }

        channel_messages[new_message_id] = new_message

        return json.dumps({
            "success": True,
            "message_record": new_message,
            "message_text": f"Message '{new_message_id}' posted to channel '{channel_id}' successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "send_channel_message",
                "description": (
                    "Posts a new text message into a specified communication channel, optionally linking it to a thread or a support ticket.\n"
                    " Purpose: Facilitates real-time broadcast and operational updates. Specifically maps to SOPs requiring the posting of the 'Initial Incident Brief' in Incident Swarms, and publishing status and impact summaries in Broadcast Updates.\n"
                    " When to use: Use this tool to send updates into active channels, such as establishing context for a newly provisioned incident swarm channel or sending major incident status updates to public announcement channels.\n"
                    " Returns: Returns a JSON string containing a success boolean, the newly created message dictionary object, and a success message text. Fails if the channel or sender does not exist."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "The unique identifier of the target channel where the message will be posted."
                        },
                        "sender_id": {
                            "type": "string",
                            "description": "The unique identifier of the user (e.g., the Incident Commander or agent) sending the message."
                        },
                        "message": {
                            "type": "string",
                            "description": "The body of the message to be broadcasted or shared in the channel."
                        },
                        "thread_id": {
                            "type": "string",
                            "description": "Optional identifier if posting this message as a reply inside a specific thread."
                        },
                        "related_ticket_id": {
                            "type": "string",
                            "description": "Optional ticket identifier if the message is directly referencing a specific support ticket."
                        }
                    },
                    "required": ["channel_id", "sender_id", "message"]
                }
            }
        }
