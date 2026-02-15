import json
from typing import Dict, Any
from tau_bench.envs.tool import Tool


class FetchChannelDetails(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_name: str,
    ) -> str:
        if not channel_name:
            return json.dumps({"error": "channel_name is required"})

        channels = data.get("channels", {})

        channel_details = None
        for _, c_details in channels.items():
            if c_details.get("name") == str(channel_name):
                channel_details = c_details
                break

        if not channel_details:
            return json.dumps({"error": f"Channel with name '{channel_name}' not found"})

        return json.dumps({
            "success": True,
            "channel": {
                "channel_id": str(channel_details["channel_id"]),
                "name": str(channel_details["name"]),
                "description": str(channel_details["description"]) if channel_details.get("description") else None,
                "ticket_id": str(channel_details["ticket_id"]) if channel_details.get("ticket_id") else None,
                "channel_type": str(channel_details["channel_type"]),
                "status": str(channel_details["status"]),
                "created_at": str(channel_details["created_at"]),
                "updated_at": str(channel_details["updated_at"]),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_channel_details",
                "description": "Fetches details of a channel. It should be used when you need to retrieve information about a specific channel.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_name": {
                            "type": "string",
                            "description": "The name of the channel",
                        },
                    },
                    "required": ["channel_name"],
                },
            },
        }
