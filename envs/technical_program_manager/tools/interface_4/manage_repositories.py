import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class ManageRepositories(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        action: str,
        repository_id: Optional[str] = None,
        repository_name: Optional[str] = None,
        description: Optional[str] = None,
        project_id: Optional[str] = None,
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

        repositories = data.get("repositories", {})
        projects = data.get("projects", {})
        pull_requests = data.get("pull_requests", {})

        if action_str == "create":
            if repository_id is not None:
                return json.dumps(
                    {
                        "success": False,
                        "error": "repository_id should not be provided when creating a repository",
                    }
                )

            if not all([repository_name, project_id]):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Create requires: repository_name, project_id",
                    }
                )

            name_str = str(repository_name).strip()
            pid = str(project_id).strip()

            # Validate project exists and status is open/in_progress
            project = projects.get(pid)
            if project is None:
                return json.dumps({"success": False, "error": f"Project '{pid}' not found"})
            if str(project.get("status", "")) not in ["open", "in_progress"]:
                return json.dumps({"success": False, "error": f"Project '{pid}' is not active. Current status: {str(project.get('status', ''))}"})

            # Duplicate name check within project
            for repo in repositories.values():
                if str(repo.get("project_id", "")) == pid and str(repo.get("repository_name", "")).lower() == name_str.lower():
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Repository with name '{name_str}' already exists",
                        }
                    )

            if repositories:
                max_id = max(int(k) for k in repositories.keys())
                new_id = str(max_id + 1)
            else:
                new_id = "1"

            new_repo = {
                "repository_id": new_id,
                "repository_name": name_str,
                "description": str(description).strip() if description else None,
                "project_id": pid,
                "created_at": timestamp,
                "updated_at": timestamp,
            }

            repositories[new_id] = new_repo

            response = {
                "repository_id": str(new_repo.get("repository_id", "")),
                "repository_name": str(new_repo.get("repository_name", "")),
                "description": str(new_repo.get("description", "")) if new_repo.get("description") else None,
                "project_id": str(new_repo.get("project_id", "")),
                "created_at": str(new_repo.get("created_at", "")),
                "updated_at": str(new_repo.get("updated_at", "")),
            }
            return json.dumps({"success": True, "repository": response})

        elif action_str == "update":
            if not repository_id:
                return json.dumps(
                    {"success": False, "error": "Update requires: repository_id"}
                )

            rid = str(repository_id).strip()
            repo = repositories.get(rid)
            if repo is None:
                return json.dumps(
                    {"success": False, "error": f"Repository '{rid}' not found"}
                )

            if not any([repository_name, description, project_id]):
                return json.dumps(
                    {
                        "success": False,
                        "error": "At least one field to update must be provided",
                    }
                )

            # Determine the effective project for validation
            if project_id is not None:
                target_pid = str(project_id).strip()
                project = projects.get(target_pid)
                if project is None:
                    return json.dumps({"success": False, "error": f"Project '{target_pid}' not found"})
                if str(project.get("status", "")) not in ["open", "in_progress"]:
                    return json.dumps({"success": False, "error": f"Project '{target_pid}' is not active. Current status: {str(project.get('status', ''))}"})
            else:
                target_pid = str(repo.get("project_id", ""))

            if repository_name is not None:
                name_val = str(repository_name).strip()
                # Duplicate name check within target project
                for r in repositories.values():
                    if str(r.get("repository_id", "")) != rid and str(r.get("project_id", "")) == target_pid and str(r.get("repository_name", "")).lower() == name_val.lower():
                        return json.dumps(
                            {
                                "success": False,
                                "error": f"Repository with name '{name_val}' already exists",
                            }
                        )
                repo["repository_name"] = name_val

            if description is not None:
                repo["description"] = str(description).strip()

            if project_id is not None:
                repo["project_id"] = target_pid

            repo["updated_at"] = timestamp

            response = {
                "repository_id": str(repo.get("repository_id", "")),
                "repository_name": str(repo.get("repository_name", "")),
                "description": str(repo.get("description", "")) if repo.get("description") else None,
                "project_id": str(repo.get("project_id", "")),
                "created_at": str(repo.get("created_at", "")),
                "updated_at": str(repo.get("updated_at", "")),
            }
            return json.dumps({"success": True, "repository": response})

        elif action_str == "delete":
            if not repository_id:
                return json.dumps(
                    {"success": False, "error": "Delete requires: repository_id"}
                )

            rid = str(repository_id).strip()
            if rid not in repositories:
                return json.dumps(
                    {"success": False, "error": f"Repository '{rid}' not found"}
                )

            # Check for open PRs (SOP 8)
            for pr in pull_requests.values():
                if str(pr.get("repository_id", "")) == rid and str(pr.get("state", "")) == "open":
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Cannot delete: repository has open pull requests",
                        }
                    )

            # Cascade cleanup: nullify FK references
            for pr in pull_requests.values():
                if pr.get("repository_id") is not None and str(pr.get("repository_id", "")) == rid:
                    pr["repository_id"] = None

            deleted_repo = repositories.pop(rid)
            return json.dumps(
                {
                    "success": True,
                    "message": f"Repository '{str(deleted_repo.get('repository_name', ''))}' has been deleted",
                }
            )

        return json.dumps({"success": False, "error": "Unexpected error"})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "manage_repositories",
                "description": "Manages repository lifecycle by creating, updating, or deleting repository records.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "The action to perform",
                            "enum": ["create", "update", "delete"],
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Unique repository identifier.",
                        },
                        "repository_name": {
                            "type": "string",
                            "description": "Repository name",
                        },
                        "description": {
                            "type": "string",
                            "description": "Repository description",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier (project_id).",
                        },
                    },
                    "required": ["action"],
                    "allOf": [
                        {
                            "if": {
                                "properties": {"action": {"enum": ["create"]}}
                            },
                            "then": {
                                "required": ["repository_name", "project_id"]
                            },
                        },
                        {
                            "if": {
                                "properties": {"action": {"enum": ["update"]}}
                            },
                            "then": {
                                "required": ["repository_id"],
                                "anyOf": [
                                    {"required": ["repository_name"]},
                                    {"required": ["description"]},
                                    {"required": ["project_id"]},
                                ],
                            },
                        },
                        {
                            "if": {
                                "properties": {"action": {"enum": ["delete"]}}
                            },
                            "then": {
                                "required": ["repository_id"]
                            },
                        },
                    ],
                },
            },
        }
