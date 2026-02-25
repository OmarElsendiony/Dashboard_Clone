import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetChannelInfo(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_id: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format for channels"}
            )

        if channel_id is None:
            return json.dumps({"success": False, "error": "channel_id is required"})

        channels = data.get("channels", {})

        channel = None
        channel_key_str = str(channel_id)

        if channel_key_str in channels:
            channel_data = channels[channel_key_str]
            if str(channel_data.get("channel_id")) == str(channel_id):
                channel = channel_data.copy()

        if not channel:
            for channel_data in channels.values():
                if str(channel_data.get("channel_id")) == str(channel_id):
                    channel = channel_data.copy()
                    break

        if not channel:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Channel with ID {channel_id} not found",
                }
            )

        # Cast all fields to match schema types
        if channel.get("channel_id") is not None:
            channel["channel_id"] = str(channel.get("channel_id"))
        if channel.get("project_id") is not None:
            channel["project_id"] = str(channel.get("project_id"))
        if channel.get("work_item_id") is not None:
            channel["work_item_id"] = str(channel.get("work_item_id"))
        if channel.get("incident_id") is not None:
            channel["incident_id"] = str(channel.get("incident_id"))
        if channel.get("channel_name") is not None:
            channel["channel_name"] = str(channel.get("channel_name"))
        if channel.get("description") is not None:
            channel["description"] = str(channel.get("description"))
        if channel.get("channel_type") is not None:
            channel["channel_type"] = str(channel.get("channel_type"))
        if channel.get("status") is not None:
            channel["status"] = str(channel.get("status"))
        if channel.get("created_at") is not None:
            channel["created_at"] = str(channel.get("created_at"))
        if channel.get("updated_at") is not None:
            channel["updated_at"] = str(channel.get("updated_at"))

        return json.dumps(
            {
                "success": True,
                "channel": channel,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_channel_info",
                "description": "Retrieve complete channel information including channel name, description, channel_type, status, linked project/incident/work item IDs, and timestamps. Use this to access channel details for verification, archival checks, and communication hub management.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "The channel ID to retrieve information for",
                        },
                    },
                    "required": ["channel_id"],
                },
            },
        }
