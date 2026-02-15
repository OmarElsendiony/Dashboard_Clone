import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateSpaceMessage(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        sender_id: str,
        message: str,
        channel_id: Optional[str] = None,
        channel_name: Optional[str] = None,
        thread_id: Optional[str] = None,
        related_ticket_id: Optional[str] = None,
    ) -> str:
        # 1. Basic data integrity check
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        def generate_id(table: Dict[str, Any]) -> str:
            return str(max([int(k) for k in table.keys()], default=0) + 1)
        # Initialize messages container if not present
        messages = data.setdefault("channel_messages", {})

        if not channel_id and not channel_name:
            return json.dumps({"success": False, "error": "Channel ID or Channel name should be provided."})

        if not sender_id:
            return json.dumps({"success": False, "error": "Sender ID is required"})

        if not message:
            return json.dumps({"success": False, "error": "Message content is required"})

        # 2. Validation: Ensure sender exists
        users = data.get("users", {})
        if sender_id not in users:
            return json.dumps({
                "success": False,
                "error": f"Sender ID '{sender_id}' does not exist in users."
            })

        # 3. Validation: Ensure channel exists (if channels are tracked in data)
        channels = data.get("channels", {})
        target_channel = next((c for c in channels.values() if c["name"] == channel_name or c["channel_id"] == channel_id), None)

        if not target_channel:
            return json.dumps({
                "success": False,
                "error": f"Channel not found for channel id {channel_id} or channel name {channel_name}"
            })
        # Validate related_ticket_id if provided
        tickets = data.get("tickets", {})
        if related_ticket_id and related_ticket_id not in tickets:
            return json.dumps({
                "success": False,
                "error": f"Related Ticket ID '{related_ticket_id}' does not exist."
            })
        # validate thread_id if provided (optional, depending on whether threads are tracked in data)
        if thread_id:
            threads = data.get("threads", {})
            if thread_id not in threads:
                return json.dumps({
                    "success": False,
                    "error": f"Thread ID '{thread_id}' does not exist."
                })
            if threads[thread_id]["channel_id"] != channel_id:
                return json.dumps({
                    "success": False,
                    "error": f"Thread ID '{thread_id}' does not belong to Channel ID '{channel_id}'."
                })

        # 4. Logic: Generate ID and Timestamps
        # Using string of length of existing messages + 1 for simple ID generation
        new_id = generate_id(messages)
        now_iso = "2026-02-02 23:59:00"

        # 5. Create the message object
        new_message = {
            "message_id": str(new_id),
            "channel_id": str(target_channel["channel_id"]),
            "thread_id": str(thread_id) if thread_id else None,
            "sender_id": str(sender_id),
            "message": str(message),
            "related_ticket_id": str(related_ticket_id) if related_ticket_id else None,
            "sent_at": now_iso,
            "created_at": now_iso,
            "updated_at": now_iso
        }

        # Save to data
        messages[new_id] = new_message

        return json.dumps({
            "success": True,
            "message_id": new_id,
            "data": new_message
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_space_message",
                "description": "Posts a new message to a specific communication channel or space, with support for threaded conversations and ticket linking. This tool facilitates internal team discussions and coordination. Use when adding a message to a channel, replying to a thread, or linking conversations to specific tickets.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "The ID of the channel where the message will be sent."
                        },
                        "sender_id": {
                            "type": "string",
                            "description": "The ID of the user sending the message."
                        },
                        "message": {
                            "type": "string",
                            "description": "The text content of the message."
                        },
                        "thread_id": {
                            "type": "string",
                            "description": "The ID of the thread, if this message is a reply."
                        },
                        "related_ticket_id": {
                            "type": "string",
                            "description": "The ID of a ticket related to this conversation."
                        },
                        "channel_name": {
                            "type": "string",
                            "description": "The name identifier for the channel where the message is sent."
                        },


                    },
                    "required": ["sender_id", "message"],
                    "oneOf": [
                            {"required": ["channel_id"]},
                            {"required": ["channel_name"]}
                        ]
                }
            }
        }
