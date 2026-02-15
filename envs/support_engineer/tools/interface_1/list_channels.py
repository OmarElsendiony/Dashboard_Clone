import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ListChannels(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_id: str,
        channel_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })

        if not user_id:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'user_id' is required."
            })

        users = data.get("users", {})
        channels = data.get("channels", {})
        channel_members = data.get("channel_members", {})

        if str(user_id) not in users:
            return json.dumps({
                "success": False,
                "error": f"Authorization Error: user_id '{user_id}' not found."
            })

        valid_channel_types = [
            "incident", "security", "general", "accounts",
            "sla", "public", "private", "direct"
        ]

        if channel_type is not None and channel_type not in valid_channel_types:
            return json.dumps({
                "success": False,
                "error": (
                    f"Invalid Argument: channel_type must be one of {valid_channel_types}."
                )
            })

        valid_statuses = ["active", "archived"]

        if status is not None and status not in valid_statuses:
            return json.dumps({
                "success": False,
                "error": (
                    f"Invalid Argument: status must be one of {valid_statuses}."
                )
            })

        member_channel_ids = set()
        for m in channel_members.values():
            if isinstance(m, dict) and str(m.get("user_id")) == str(user_id):
                member_channel_ids.add(str(m.get("channel_id")))

        accessible_channels = []

        for ch in channels.values():
            if not isinstance(ch, dict):
                continue

            if status is not None and ch.get("status") != status:
                continue

            if channel_type is not None and ch.get("channel_type") != channel_type:
                continue

            cid = str(ch.get("channel_id"))
            ctype = ch.get("channel_type")

            if ctype in ["private", "direct"] and cid not in member_channel_ids:
                continue

            accessible_channels.append(ch)

        accessible_channels.sort(
            key=lambda x: (str(x.get("name", "")).lower(), str(x.get("channel_id", "")))
        )

        return json.dumps({
            "success": True,
            "channels": accessible_channels,
            "message": "Accessible channels retrieved successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_channels",
                "description": (
                    "Lists Slack channels that a user can access, including public channels and "
                    "private or direct channels where the user is a member. Use this to discover "
                    "available Slack channels, optionally filtering by channel type or status."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "Slack user identifier."
                        },
                        "channel_type": {
                            "type": "string",
                            "enum": [
                                "incident", "security", "general", "accounts",
                                "sla", "public", "private", "direct"
                            ],
                            "description": "Filter channels by type (optional )."
                        },
                        "status": {
                            "type": "string",
                            "enum": ["active", "archived"],
                            "description": "Filter channels by status (optional )."
                        }
                    },
                    "required": ["user_id"]
                }
            }
        }
