import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class ManageProject(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        action: str,
        project_id: Optional[str] = None,
        project_key: Optional[str] = None,
        project_name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        project_owner_user_id: Optional[str] = None,
    ) -> str:
        timestamp = "2026-02-11T23:59:00"

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        action_str = str(action).strip().lower()
        valid_actions = ["create", "update", "delete"]
        if action_str not in valid_actions:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid action '{action_str}'. Valid values: {', '.join(valid_actions)}",
                }
            )

        projects = data.get("projects", {})
        users = data.get("users", {})
        valid_statuses = ["open", "in_progress", "closed"]

        if action_str == "create":
            if project_id is not None:
                return json.dumps(
                    {
                        "success": False,
                        "error": "project_id should not be provided when creating a project",
                    }
                )

            if not all([project_key, project_name, project_owner_user_id]):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Create requires: project_key, project_name, project_owner_user_id",
                    }
                )

            key_str = str(project_key).strip()
            name_str = str(project_name).strip()
            owner_str = str(project_owner_user_id).strip()

            if not key_str or not name_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Create requires: project_key, project_name, project_owner_user_id",
                    }
                )

            # Validate owner exists and is active
            owner = users.get(owner_str)
            if owner is None:
                return json.dumps({"success": False, "error": f"User '{owner_str}' not found"})
            if str(owner.get("status", "")) != "active":
                return json.dumps({"success": False, "error": f"User '{owner_str}' is not active. Current status: {str(owner.get('status', ''))}"})

            for proj in projects.values():
                if str(proj.get("project_key", "")).lower() == key_str.lower():
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Project with key '{key_str}' already exists",
                        }
                    )
                if str(proj.get("project_name", "")).lower() == name_str.lower():
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Project with name '{name_str}' already exists",
                        }
                    )

            if projects:
                max_id = max(int(k) for k in projects.keys())
                new_id = str(max_id + 1)
            else:
                new_id = "1"

            status_str = "open"
            if status is not None:
                status_str = str(status).strip()
                if status_str not in valid_statuses:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Invalid status '{status_str}'. Valid values: {', '.join(valid_statuses)}",
                        }
                    )

            new_project = {
                "project_id": new_id,
                "project_key": key_str,
                "project_name": name_str,
                "description": str(description).strip() if description else None,
                "status": status_str,
                "project_owner_user_id": owner_str,
                "created_at": timestamp,
                "updated_at": timestamp,
            }

            projects[new_id] = new_project

            response = {
                "project_id": str(new_project.get("project_id", "")),
                "project_key": str(new_project.get("project_key", "")),
                "project_name": str(new_project.get("project_name", "")),
                "description": str(new_project.get("description", "")) if new_project.get("description") else None,
                "status": str(new_project.get("status", "")),
                "project_owner_user_id": str(new_project.get("project_owner_user_id", "")),
                "created_at": str(new_project.get("created_at", "")),
                "updated_at": str(new_project.get("updated_at", "")),
            }
            return json.dumps({"success": True, "project": response})

        elif action_str == "update":
            if not project_id:
                return json.dumps(
                    {"success": False, "error": "Update requires: project_id"}
                )

            pid = str(project_id).strip()
            project = projects.get(pid)
            if project is None:
                return json.dumps(
                    {"success": False, "error": f"Project '{pid}' not found"}
                )

            if not any([project_key, project_name, description, status, project_owner_user_id]):
                return json.dumps(
                    {
                        "success": False,
                        "error": "At least one field to update must be provided",
                    }
                )

            # Block updates if project is closed
            current_status = str(project.get("status", ""))
            if current_status == "closed":
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Cannot update project with status 'closed'",
                    }
                )

            if project_key is not None:
                key_val = str(project_key).strip()
                for proj in projects.values():
                    if str(proj.get("project_id", "")) != pid and str(proj.get("project_key", "")).lower() == key_val.lower():
                        return json.dumps(
                            {
                                "success": False,
                                "error": f"Project with key '{key_val}' already exists",
                            }
                        )
                project["project_key"] = key_val

            if project_name is not None:
                name_val = str(project_name).strip()
                for proj in projects.values():
                    if str(proj.get("project_id", "")) != pid and str(proj.get("project_name", "")).lower() == name_val.lower():
                        return json.dumps(
                            {
                                "success": False,
                                "error": f"Project with name '{name_val}' already exists",
                            }
                        )
                project["project_name"] = name_val

            if description is not None:
                project["description"] = str(description).strip()

            if status is not None:
                status_val = str(status).strip()
                if status_val not in valid_statuses:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Invalid status '{status_val}'. Valid values: {', '.join(valid_statuses)}",
                        }
                    )
                project["status"] = status_val

            if project_owner_user_id is not None:
                owner_val = str(project_owner_user_id).strip()
                owner = users.get(owner_val)
                if owner is None:
                    return json.dumps({"success": False, "error": f"User '{owner_val}' not found"})
                if str(owner.get("status", "")) != "active":
                    return json.dumps({"success": False, "error": f"User '{owner_val}' is not active. Current status: {str(owner.get('status', ''))}"})
                project["project_owner_user_id"] = owner_val

            project["updated_at"] = timestamp

            response = {
                "project_id": str(project.get("project_id", "")),
                "project_key": str(project.get("project_key", "")),
                "project_name": str(project.get("project_name", "")),
                "description": str(project.get("description", "")) if project.get("description") else None,
                "status": str(project.get("status", "")),
                "project_owner_user_id": str(project.get("project_owner_user_id", "")),
                "created_at": str(project.get("created_at", "")),
                "updated_at": str(project.get("updated_at", "")),
            }
            return json.dumps({"success": True, "project": response})

        elif action_str == "delete":
            if not project_id:
                return json.dumps(
                    {"success": False, "error": "Delete requires: project_id"}
                )

            pid = str(project_id).strip()
            if pid not in projects:
                return json.dumps(
                    {"success": False, "error": f"Project '{pid}' not found"}
                )

            # Check for related entities
            work_items = data.get("work_items", {})
            sprints = data.get("sprints", {})
            project_members = data.get("project_members", {})
            channels = data.get("channels", {})
            repositories = data.get("repositories", {})
            documents = data.get("documents", {})

            for wi in work_items.values():
                if str(wi.get("project_id", "")) == pid:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Cannot delete: project has associated issues",
                        }
                    )

            for s in sprints.values():
                if str(s.get("project_id", "")) == pid:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Cannot delete: project has associated sprints",
                        }
                    )

            for pm in project_members.values():
                if str(pm.get("project_id", "")) == pid:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Cannot delete: project has associated members",
                        }
                    )

            for ch in channels.values():
                if str(ch.get("project_id", "")) == pid:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Cannot delete: project has associated channels",
                        }
                    )

            for repo in repositories.values():
                if str(repo.get("project_id", "")) == pid:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Cannot delete: project has associated repositories",
                        }
                    )

            for doc in documents.values():
                if str(doc.get("project_id", "")) == pid:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Cannot delete: project has associated documents",
                        }
                    )

            deleted_project = projects.pop(pid)
            return json.dumps(
                {
                    "success": True,
                    "message": f"Project '{str(deleted_project.get('project_name', ''))}' has been deleted",
                }
            )

        return json.dumps({"success": False, "error": "Unexpected error"})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "manage_project",
                "description": "Manages project lifecycle by creating, updating, or deleting project records.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "The action to perform",
                            "enum": ["create", "update", "delete"],
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Unique project identifier.",
                        },
                        "project_key": {
                            "type": "string",
                            "description": "Unique project key",
                        },
                        "project_name": {
                            "type": "string",
                            "description": "Project name",
                        },
                        "description": {
                            "type": "string",
                            "description": "Project description",
                        },
                        "status": {
                            "type": "string",
                            "description": "Project status. Default for new projects is 'open'.",
                            "enum": ["open", "in_progress", "closed"],
                        },
                        "project_owner_user_id": {
                            "type": "string",
                            "description": "User identifier of the project owner.",
                        },
                    },
                    "required": ["action"],
                    "allOf": [
                        {
                            "if": {
                                "properties": {"action": {"enum": ["create"]}}
                            },
                            "then": {
                                "required": ["project_key", "project_name", "project_owner_user_id"]
                            },
                        },
                        {
                            "if": {
                                "properties": {"action": {"enum": ["update"]}}
                            },
                            "then": {
                                "required": ["project_id"],
                                "anyOf": [
                                    {"required": ["project_key"]},
                                    {"required": ["project_name"]},
                                    {"required": ["description"]},
                                    {"required": ["status"]},
                                    {"required": ["project_owner_user_id"]},
                                ],
                            },
                        },
                        {
                            "if": {
                                "properties": {"action": {"enum": ["delete"]}}
                            },
                            "then": {
                                "required": ["project_id"]
                            },
                        },
                    ],
                },
            },
        }
