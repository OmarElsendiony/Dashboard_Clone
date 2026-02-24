import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetChannel(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_name: Optional[str] = None,
        channel_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        channels_dict = data.get("channels", {})

        if not channel_name and not channel_id:
            return json.dumps(
                {
                    "success": False,
                    "error": "Either channel_name or channel_id must be provided",
                }
            )

        target_channel = None
        target_channel_id = None

        if channel_id:
            channel_id_str = str(channel_id).strip()
            if channel_id_str in channels_dict:
                target_channel = channels_dict[channel_id_str]
                target_channel_id = channel_id_str
            else:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Channel with ID '{channel_id_str}' not found",
                    }
                )

        if not target_channel and channel_name:
            search_name = str(channel_name).strip().lower()
            for c_id, c_data in channels_dict.items():
                if str(c_data.get("name", "")).strip().lower() == search_name:
                    target_channel = c_data
                    target_channel_id = c_id
                    break

            if not target_channel:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Channel with name '{channel_name}' not found",
                    }
                )

        if not target_channel:
            return json.dumps({"success": False, "error": "Channel not found"})

        response = {
            "channel_id": str(target_channel_id),
            "name": str(target_channel.get("name", "")),
            "description": (
                str(target_channel.get("description", ""))
                if target_channel.get("description")
                else None
            ),
            "ticket_id": (
                str(target_channel.get("ticket_id", ""))
                if target_channel.get("ticket_id")
                else None
            ),
            "channel_type": str(target_channel.get("channel_type", "general")),
            "status": str(target_channel.get("status", "active")),
            "created_at": str(target_channel.get("created_at", None)),
            "updated_at": str(target_channel.get("updated_at", None)),
        }

        return json.dumps({"success": True, "channel": response})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_channel",
                "description": (
                    "Retrieves communication channel details by name or ID. "
                    "This function verifies channel existence and status before message posting. "
                    "Use this before sending SLA violation alerts, incident notifications, "
                    "security fix notifications, or internal status updates "
                    "to ensure the correct communication channel is active and available."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_name": {
                            "type": "string",
                            "description": "The name of the channel to retrieve",
                        },
                        "channel_id": {
                            "type": "string",
                            "description": "The unique identifier of the channel to retrieve.",
                        },
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["channel_name"]},
                        {"required": ["channel_id"]}
                    ]
                },
            },
        }
