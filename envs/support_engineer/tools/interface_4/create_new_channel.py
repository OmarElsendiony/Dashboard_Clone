import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateNewChannel(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        name: str,
        channel_type: str,
        description: Optional[str] = None,
        ticket_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not name:
            return json.dumps({"success": False, "error": "name is required"})

        if not channel_type:
            return json.dumps(
                {"success": False, "error": "channel_type is required"}
            )

        valid_channel_types = [
            "public", "private", "direct"
        ]
        if channel_type not in valid_channel_types:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid channel_type '{channel_type}'. Valid values: {', '.join(valid_channel_types)}",
                }
            )

        channels = data.get("channels", {})
        tickets = data.get("tickets", {})

        if ticket_id is not None:
            if str(ticket_id) not in tickets:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Ticket with id '{ticket_id}' not found",
                    }
                )

        for channel in channels.values():
            if channel.get("name", "").lower() == name.lower():
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Channel with name '{name}' already exists (case-insensitive duplicate)",
                    }
                )

        if channels:
            max_id = max(int(k) for k in channels.keys())
            new_channel_id = str(max_id + 1)
        else:
            new_channel_id = "1"

        static_timestamp = "2026-02-02 23:59:00"

        new_channel = {
            "channel_id": new_channel_id,
            "name": name,
            "description": description,
            "ticket_id": ticket_id,
            "channel_type": channel_type,
            "status": "active",
            "created_at": static_timestamp,
            "updated_at": static_timestamp,
        }

        channels[new_channel_id] = new_channel

        return json.dumps({"success": True, "channel": new_channel})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_new_channel",
                "description": "Create a new communication channel for team collaboration.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Channel name",
                        },
                        "channel_type": {
                            "type": "string",
                            "description": "Type of channel",
                            "enum": ["public", "private", "direct"],
                        },
                        "description": {
                            "type": "string",
                            "description": "Channel description",
                        },
                        "ticket_id": {
                            "type": "string",
                            "description": "Ticket identifier this channel relates to",
                        },
                    },
                    "required": ["name", "channel_type"],
                },
            },
        }
