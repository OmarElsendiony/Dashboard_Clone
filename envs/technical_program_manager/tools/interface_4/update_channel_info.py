import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class UpdateChannelInfo(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_id: str,
        channel_name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        timestamp = "2026-02-11T23:59:00"

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not channel_id:
            return json.dumps(
                {"success": False, "error": "Update requires: channel_id"}
            )

        if not any([channel_name, description, status]):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one field to update must be provided",
                }
            )

        valid_statuses = ["active", "archived"]

        cid = str(channel_id).strip()
        channels = data.get("channels", {})

        channel = channels.get(cid)
        if channel is None:
            return json.dumps(
                {"success": False, "error": f"Channel '{cid}' not found"}
            )

        if channel_name is not None:
            name_val = str(channel_name).strip()
            for ch in channels.values():
                if str(ch.get("channel_id", "")) != cid and str(ch.get("channel_name", "")).lower() == name_val.lower():
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Channel with name '{name_val}' already exists",
                        }
                    )
            channel["channel_name"] = name_val

        if description is not None:
            channel["description"] = str(description).strip()

        if status is not None:
            status_val = str(status).strip()
            if status_val not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status '{status_val}'. Valid values: {', '.join(valid_statuses)}",
                    }
                )
            channel["status"] = status_val

        channel["updated_at"] = timestamp

        response = {
            "channel_id": str(channel.get("channel_id", "")),
            "channel_name": str(channel.get("channel_name", "")),
            "project_id": str(channel.get("project_id", "")) if channel.get("project_id") else None,
            "description": str(channel.get("description", "")) if channel.get("description") else None,
            "status": str(channel.get("status", "")),
            "created_at": str(channel.get("created_at", "")),
            "updated_at": str(channel.get("updated_at", "")),
        }
        return json.dumps({"success": True, "channel": response})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_channel_info",
                "description": "Updates an existing communication channel.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "Unique channel identifier.",
                        },
                        "channel_name": {
                            "type": "string",
                            "description": "Channel name",
                        },
                        "description": {
                            "type": "string",
                            "description": "Channel description",
                        },
                        "status": {
                            "type": "string",
                            "description": "Channel status",
                            "enum": ["active", "archived"],
                        },
                    },
                    "required": ["channel_id"],
                    "anyOf": [
                        {"required": ["channel_name"]},
                        {"required": ["description"]},
                        {"required": ["status"]},
                    ],
                },
            },
        }
