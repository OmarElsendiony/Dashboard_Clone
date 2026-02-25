import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ConstructChannel(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_name: str,
        status: str,
        project_id: str,
        description: Optional[str] = None,
    ) -> str:
        timestamp = "2026-02-11T23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            """Generate a new unique ID for a record."""
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        for param_name, param_value in [
            ("channel_name", channel_name),
            ("status", status),
            ("project_id", project_id),
        ]:
            if not param_value or not str(param_value).strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Missing required parameter: '{param_name}'",
                    }
                )

        channel_name_str = str(channel_name).strip()
        status_str = str(status).strip().lower()
        project_id_str = str(project_id).strip()
        description_str = str(description).strip() if description else None

        valid_statuses = ["active"]
        if status_str not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Invalid status '{status_str}'. "
                        f"Must be one of: {', '.join(valid_statuses)}"
                    ),
                }
            )

        channels_dict = data.get("channels", {})
        projects_dict = data.get("projects", {})

        if project_id_str not in projects_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Project with ID '{project_id_str}' not found",
                }
            )

        project = projects_dict[project_id_str]
        if not isinstance(project, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Invalid project data structure for ID '{project_id_str}'"
                    ),
                }
            )

        for c_id, c_data in channels_dict.items():
            if not isinstance(c_data, dict):
                continue
            if str(c_data.get("name", "")).strip().lower() == channel_name_str.lower():
                return json.dumps(
                    {
                        "success": False,
                        "error": (
                            f"A channel with the name '{channel_name_str}' already exists "
                            f"(channel_id: {c_id})"
                        ),
                    }
                )

        new_channel_id = generate_id(channels_dict)

        new_channel = {
            "channel_id": str(new_channel_id),
            "channel_name": str(channel_name_str),
            "description": str(description_str) if description_str else None,
            "channel_type": "room",
            "status": str(status_str),
            "project_id": str(project_id_str),
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        channels_dict[new_channel_id] = new_channel

        new_channel_return = new_channel.copy()
        new_channel_return.pop("channel_type")

        return json.dumps(
            {
                "success": True,
                "channel": new_channel_return,
                "message": (
                    f"Channel '{channel_name_str}' created successfully "
                    f"with ID '{new_channel_id}' for project '{project_id_str}'"
                ),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "construct_channel",
                "description": "Creates a new communication channel for a project. Channel names must be unique across the system. "
                "Use this during project setup to establish the primary communication space for a project, or during project kickoff when no active channel "
                "exists for the project yet. Always creates channels of type 'room'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_name": {
                            "type": "string",
                            "description": "The name of the channel to create. ",
                        },
                        "status": {
                            "type": "string",
                            "description": "The status of the channel. ",
                            "enum": ["active"],
                        },
                        "project_id": {
                            "type": "string",
                            "description": "The unique identifier of the project this channel belongs to. "
                            "Sourced from create_project or fetch_project.",
                        },
                        "description": {
                            "type": "string",
                            "description": "A brief description of the channel's purpose.",
                        },
                    },
                    "required": ["channel_name", "status", "project_id"],
                },
            },
        }
