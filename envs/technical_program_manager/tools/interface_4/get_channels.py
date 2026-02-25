import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class GetChannels(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_id: Optional[str] = None,
        channel_name: Optional[str] = None,
        status: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not any([channel_id, channel_name, status, project_id]):
            return json.dumps({
                "success": False,
                "error": "At least one filter parameter must be provided",
            })

        if status is not None:
            status_str = str(status).strip()
            valid_statuses = ["active", "archived"]
            if status_str not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status '{status_str}'. Valid values: {', '.join(valid_statuses)}",
                    }
                )
        else:
            status_str = None

        channel_id_str = str(channel_id).strip() if channel_id else None
        channel_name_str = str(channel_name).strip() if channel_name else None
        project_id_str = str(project_id).strip() if project_id else None

        channels = data.get("channels", {})
        projects = data.get("projects", {})

        if project_id_str is not None and project_id_str not in projects:
            return json.dumps({"success": False, "error": f"Project '{project_id_str}' not found"})

        results = []
        for channel in channels.values():
            if channel_id_str is not None and str(channel.get("channel_id", "")) != channel_id_str:
                continue

            if channel_name_str is not None and channel_name_str.lower() != str(channel.get("channel_name", "")).lower():
                continue

            if status_str is not None and str(channel.get("status", "")) != status_str:
                continue

            if project_id_str is not None and str(channel.get("project_id", "")) != project_id_str:
                continue

            filtered_channel = {
                "channel_id": str(channel.get("channel_id", "")),
                "channel_name": str(channel.get("channel_name", "")),
                "description": str(channel.get("description", "")) if channel.get("description") else None,
                "status": str(channel.get("status", "")),
                "project_id": str(channel.get("project_id", "")) if channel.get("project_id") else None,
                "created_at": str(channel.get("created_at", "")),
                "updated_at": str(channel.get("updated_at", "")),
            }
            results.append(filtered_channel)
        results.sort(key=lambda x: int(x["channel_id"]))
        return json.dumps({"success": True, "channels": results, "count": int(len(results))})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_channels",
                "description": "Retrieves communication channel records based on optional filter criteria.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "Filter by the exact unique channel identifier (channel_id).",
                        },
                        "channel_name": {
                            "type": "string",
                            "description": "Filter by channel name (exact, case-insensitive).",
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by channel status",
                            "enum": ["active", "archived"],
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Filter by the project identifier (project_id).",
                        },
                    },
                    "anyOf": [
                        {"required": ["channel_id"]},
                        {"required": ["channel_name"]},
                        {"required": ["status"]},
                        {"required": ["project_id"]},
                    ],
                    "required": [],
                },
            },
        }
