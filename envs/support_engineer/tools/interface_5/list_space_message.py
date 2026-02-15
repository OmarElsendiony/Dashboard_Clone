import json
from typing import Dict, Optional
from tau_bench.envs.tool import Tool


class ListSpaceMessage(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, object],
        space_id: str,
        ticket_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format for space messages"}
            )

        if not space_id:
            return json.dumps({"success": False, "error": "space_id is required"})

        channels = data.get("channels", {})
        channel_messages = data.get("channel_messages", {})

        if space_id not in channels:
            return json.dumps(
                {"success": False, "error": f"Space (channel) with ID {space_id} not found"}
            )

        channel = channels[space_id]

        if ticket_id:
            if str(channel.get("ticket_id")) != str(ticket_id):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Space (channel) {space_id} is not associated with ticket {ticket_id}",
                    }
                )

        messages = [
            message
            for message in channel_messages.values()
            if str(message.get("channel_id")) == str(space_id)
        ]

        messages.sort(key=lambda x: x.get("sent_at", ""))

        return json.dumps(
            {
                "success": True,
                "space_id": str(space_id),
                "space_name": channel.get("name"),
                "ticket_id": str(channel.get("ticket_id")) if channel.get("ticket_id") else None,
                "messages": messages,
                "total_messages": len(messages),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, object]:
        return {
            "type": "function",
            "function": {
                "name": "list_space_message",
                "description": "List all messages in an incident collaboration space (channel). Use this to review the incident space to confirm no unanswered questions remain before closing, check message history, and verify communication status. space_id is required. Optionally filter by ticket_id to ensure the space is associated with the correct ticket. Returns messages sorted chronologically by sent_at timestamp (oldest first) for easy review of conversation flow.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "space_id": {
                            "type": "string",
                            "description": "ID of the space (channel) to list messages from (required)",
                        },
                        "ticket_id": {
                            "type": "string",
                            "description": "Optional ticket ID to validate the space is associated with this ticket (optional)",
                        },
                    },
                    "required": ["space_id"],
                },
            },
        }
