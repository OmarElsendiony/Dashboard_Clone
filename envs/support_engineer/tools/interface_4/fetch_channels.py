import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class FetchChannels(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_type: Optional[str] = None,
        name: Optional[str] = None,
        ticket_id: Optional[str] = None,
        status: str = "active",
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

        if channel_type is not None:
            valid_channel_types = ["public", "private", "direct"]
            if channel_type not in valid_channel_types:
                return json.dumps({
                    "success": bool(False),
                    "error": str(
                        f"Invalid channel_type '{channel_type}'. Valid values: {', '.join(valid_channel_types)}"
                    ),
                })

        if status is not None:
            valid_statuses = ["active"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": bool(False),
                    "error": str(f"Invalid status '{status}'. Valid values: active"),
                })

        channels = data.get("channels", {})

        results = []
        for channel in channels.values():
            if channel_type is not None and channel.get("channel_type") != channel_type:
                continue

            if name is not None and name.lower() not in channel.get("name", "").lower():
                continue

            if ticket_id is not None:
                channel_ticket_id = channel.get("ticket_id")
                if channel_ticket_id is None or str(channel_ticket_id) != str(ticket_id):
                    continue

            if status is not None and channel.get("status") != status:
                continue

            out_channel = {
                "channel_id": str(channel.get("channel_id", "")),
                "name": str(channel.get("name", "")),
                "description": None if channel.get("description") is None else str(channel.get("description")),
                "ticket_id": None if channel.get("ticket_id") is None else str(channel.get("ticket_id")),
                "channel_type": str(channel.get("channel_type", "")),
                "status": str(channel.get("status", "active")),
                "created_at": str(channel.get("created_at", "")),
                "updated_at": str(channel.get("updated_at", "")),
            }
            results.append(out_channel)

        return json.dumps({
            "success": bool(True),
            "channels": results,
            "count": int(len(results)),
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_channels",
                "description": "Lists communication channels, optionally filtered by type, name, ticket, or status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_type": {
                            "type": "string",
                            "description": "Filter by channel type.",
                            "enum": ["public", "private", "direct"],
                        },
                        "name": {
                            "type": "string",
                            "description": "Filter by channel name substring.",
                        },
                        "ticket_id": {
                            "type": "string",
                            "description": "Filter by associated ticket identifier.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by channel status. Default: active.",
                            "enum": ["active"],
                        },
                    },
                    "required": [],
                },
            },
        }
