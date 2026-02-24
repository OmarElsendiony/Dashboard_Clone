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
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return json.dumps({
                    "success": bool(False),
                    "error": str("Wrong data format"),
                })
        if not isinstance(data, dict):
            return json.dumps({
                "success": bool(False),
                "error": str("Wrong data format"),
            })

        name_str = str(name).strip() if name is not None else ""
        if not name_str:
            return json.dumps({
                "success": bool(False),
                "error": str("name is required"),
            })

        channel_type_str = str(channel_type).strip() if channel_type is not None else ""
        if not channel_type_str:
            return json.dumps({
                "success": bool(False),
                "error": str("channel_type is required"),
            })

        valid_channel_types = ["public", "private", "direct"]
        if channel_type_str not in valid_channel_types:
            return json.dumps({
                "success": bool(False),
                "error": str(
                    f"Invalid channel_type '{channel_type_str}'. Valid values: {', '.join(valid_channel_types)}"
                ),
            })

        channels = data.get("channels", {})
        tickets = data.get("tickets", {})

        if ticket_id is not None:
            ticket_id_str = str(ticket_id).strip()
            if ticket_id_str and ticket_id_str not in tickets:
                return json.dumps({
                    "success": bool(False),
                    "error": str(f"Ticket with id '{ticket_id}' not found"),
                })

        for channel in channels.values():
            if channel.get("name", "").lower() == name_str.lower():
                return json.dumps({
                    "success": bool(False),
                    "error": str(
                        f"Channel with name '{name_str}' already exists (case-insensitive duplicate)"
                    ),
                })

        if channels:
            max_id = max(int(k) for k in channels.keys())
            new_channel_id = str(max_id + 1)
        else:
            new_channel_id = str(1)

        static_timestamp = str("2026-02-02 23:59:00")

        new_channel = {
            "channel_id": str(new_channel_id),
            "name": str(name_str),
            "description": str(description) if description is not None else None,
            "ticket_id": str(ticket_id).strip() if ticket_id is not None else None,
            "channel_type": str(channel_type_str),
            "status": str("active"),
            "created_at": str(static_timestamp),
            "updated_at": str(static_timestamp),
        }

        channels[new_channel_id] = new_channel

        out_channel = {
            "channel_id": str(new_channel["channel_id"]),
            "name": str(new_channel["name"]),
            "description": None if new_channel["description"] is None else str(new_channel["description"]),
            "ticket_id": None if new_channel["ticket_id"] is None else str(new_channel["ticket_id"]),
            "channel_type": str(new_channel["channel_type"]),
            "status": str(new_channel["status"]),
            "created_at": str(new_channel["created_at"]),
            "updated_at": str(new_channel["updated_at"]),
        }
        return json.dumps({"success": bool(True), "channel": out_channel})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_new_channel",
                "description": "Creates a new communication channel for team collaboration.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Channel name.",
                        },
                        "channel_type": {
                            "type": "string",
                            "description": "Type of channel.",
                            "enum": ["public", "private", "direct"],
                        },
                        "description": {
                            "type": "string",
                            "description": "Channel description.",
                        },
                        "ticket_id": {
                            "type": "string",
                            "description": "Ticket identifier this channel relates to.",
                        },
                    },
                    "required": ["name", "channel_type"],
                },
            },
        }
