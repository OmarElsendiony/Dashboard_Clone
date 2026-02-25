import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class CreateNewChannel(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_name: str,
        project_id: str,
        description: Optional[str] = None,
    ) -> str:
        timestamp = "2026-02-11T23:59:00"

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not all([channel_name, project_id]):
            return json.dumps(
                {
                    "success": False,
                    "error": "Create requires: channel_name, project_id",
                }
            )

        name_str = str(channel_name).strip()
        pid = str(project_id).strip()

        channels = data.get("channels", {})
        projects = data.get("projects", {})

        # Validate project exists and status is open/in_progress
        project = projects.get(pid)
        if project is None:
            return json.dumps({"success": False, "error": f"Project '{pid}' not found"})
        if str(project.get("status", "")) not in ["open", "in_progress"]:
            return json.dumps({"success": False, "error": f"Project '{pid}' is not active. Current status: {str(project.get('status', ''))}"})

        for ch in channels.values():
            if str(ch.get("channel_name", "")).lower() == name_str.lower():
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Channel with name '{name_str}' already exists",
                    }
                )

        if channels:
            max_id = max(int(k) for k in channels.keys())
            new_id = str(max_id + 1)
        else:
            new_id = "1"

        new_channel = {
            "channel_id": new_id,
            "channel_name": name_str,
            "description": str(description).strip() if description else None,
            "project_id": pid,
            "status": "active",
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        channels[new_id] = new_channel

        response = {
            "channel_id": str(new_channel.get("channel_id", "")),
            "channel_name": str(new_channel.get("channel_name", "")),
            "description": str(new_channel.get("description", "")) if new_channel.get("description") else None,
            "project_id": str(new_channel.get("project_id", "")),
            "status": str(new_channel.get("status", "")),
            "created_at": str(new_channel.get("created_at", "")),
            "updated_at": str(new_channel.get("updated_at", "")),
        }
        return json.dumps({"success": True, "channel": response})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_new_channel",
                "description": "Creates a new communication channel.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_name": {
                            "type": "string",
                            "description": "Channel name",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Unique project identifier.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Channel description",
                        },
                    },
                    "required": ["channel_name", "project_id"],
                },
            },
        }
