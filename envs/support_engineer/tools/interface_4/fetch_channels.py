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
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if channel_type is not None:
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

        if status is not None:
            valid_statuses = ["active"]
            if status not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status '{status}'. Valid values: active",
                    }
                )

        channels = data.get("channels", {})

        results = []
        for channel in channels.values():
            if channel_type is not None and channel.get("channel_type") != channel_type:
                continue

            if name is not None and name.lower() not in channel.get("name", "").lower():
                continue

            if ticket_id is not None:
                channel_ticket_id = channel.get("ticket_id")
                if channel_ticket_id is None or str(channel_ticket_id) != str(
                    ticket_id
                ):
                    continue

            if status is not None and channel.get("status") != status:
                continue

            results.append(channel)

        return json.dumps({"success": True, "channels": results, "count": len(results)})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_channels",
                "description": "List communication channels, optionally filtered by type, name, ticket, or status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_type": {
                            "type": "string",
                            "description": "Filter by channel type",
                            "enum": ["public", "private", "direct"],
                        },
                        "name": {
                            "type": "string",
                            "description": "Filter by channel name substring",
                        },
                        "ticket_id": {
                            "type": "string",
                            "description": "Filter by associated ticket identifier",
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by channel status",
                            "enum": ["active"],
                        },
                    },
                    "required": [],
                },
            },
        }
