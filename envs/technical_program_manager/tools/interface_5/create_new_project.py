import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool
import hashlib


class CreateNewProject(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        project_name: str,
        owner_identifier: Dict[str, str],
        description: Optional[str] = None,
        status: str = "open",
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        now = "2026-02-11T23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            return str(max([int(k) for k in table.keys()], default=0) + 1)

        projects = data.get("projects", {})
        users = data.get("users", {})

        if not project_name or not project_name.strip():
            return json.dumps({"success": False, "error": "Project name is required."})

        if len(project_name) > 255:
            return json.dumps(
                {
                    "success": False,
                    "error": "Project name exceeds maximum length of 255 characters.",
                }
            )

        if any(p["project_name"] == project_name for p in projects.values()):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Project with name '{project_name}' already exists.",
                }
            )

        if not description:
            description = f"Core project container for {project_name}."

        valid_statuses = [
            "open",
            "in_progress",
            "blocked",
            "closed",
        ]
        if status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}",
                }
            )

        owner_id = None
        if owner_identifier:
            if not isinstance(owner_identifier, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "owner_identifier must be a dictionary object.",
                    }
                )
            owner_email = owner_identifier.get("email")
            owner_username = owner_identifier.get("username")

            # Find user based on provided identifiers
            owner_data = next(
                (
                    u
                    for u in users.values()
                    if (owner_email and u["email"] == owner_email)
                    or (owner_username and u["username"] == owner_username)
                ),
                None,
            )

            if not owner_data:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Project owner not found with provided identifiers.",
                    }
                )
            if owner_data and owner_data["role"] != "technical_program_manager":
                return json.dumps(
                    {
                        "success": False,
                        "error": "Owner must be a Technical Program Manager.",
                    }
                )

            owner_id = owner_data["user_id"]
        else:
            return json.dumps(
                {
                    "success": False,
                    "error": "owner_identifier is required for project initialization.",
                }
            )

        new_project_id = generate_id(projects)

        # Generate a project key (max 20 characters)
        key = hashlib.md5(project_name.encode()).hexdigest()
        key1 = hashlib.sha1(project_name.encode()).hexdigest()
        space = abs(len(key) - len(key1))
        project_key = (key[-space:] + key1[-space:])[:20]
        new_project = {
            "project_id": new_project_id,
            "project_key": project_key,
            "project_name": project_name,
            "description": description,
            "status": status,
            "project_owner_user_id": str(owner_id),
            "created_at": now,
            "updated_at": now,
            "closed_at": None,
        }

        projects[new_project_id] = new_project

        # Type cast all values and build response object
        typed_project = {}
        for key, value in new_project.items():
            if value is None:
                typed_project[key] = None
            elif key in [
                "project_id",
                "project_key",
                "project_name",
                "description",
                "status",
                "project_owner_user_id",
                "created_at",
                "updated_at",
                "closed_at",
            ]:
                typed_project[key] = str(value) if value is not None else None
            elif isinstance(value, bool):
                typed_project[key] = bool(value)
            elif isinstance(value, int):
                typed_project[key] = int(value)
            elif isinstance(value, float):
                typed_project[key] = float(value)
            elif isinstance(value, list):
                typed_project[key] = list(value)
            elif isinstance(value, dict):
                typed_project[key] = dict(value)
            else:
                typed_project[key] = value

        response = {
            "success": bool(True),
            "message": str("Project initialized and environment setup completed."),
            "project": dict(typed_project),
        }

        return json.dumps(response)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_new_project",
                "description": "This tool establishes the primary container to which all subsequent work items, repositories, and communication channels must be linked. Use this tool ONLY during the 'Project Initialization' phase. It is the mandatory first step before seeding a backlog, bootstrapping repositories, or provisioning collaboration hubs.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "maxLength": 255,
                            "description": "The unique name of the new project (max 255 characters).",
                        },
                        "description": {
                            "type": "string",
                            "description": "A high-level explanation of the project's purpose.",
                        },
                        "status": {
                            "type": "string",
                            "enum": [
                                "open",
                                "in_progress",
                                "blocked",
                                "closed",
                            ],
                            "default": "open",
                            "description": "The initial status of the project.",
                        },
                        "owner_identifier": {
                            "type": "object",
                            "description": "Metadata used to identify the user who will be the project owner.",
                            "properties": {
                                "username": {
                                    "type": "string",
                                    "description": "The unique username of the owner.",
                                },
                                "email": {
                                    "type": "string",
                                    "description": "The unique email address of the owner.",
                                },
                            },
                        },
                    },
                    "required": ["project_name", "owner_identifier"],
                },
            },
        }
