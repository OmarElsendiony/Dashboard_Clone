import json
from typing import Any, Dict

from tau_bench.envs.tool import Tool


class ManageProjectMembers(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        action: str,
        user_id: str,
        project_id: str,
    ) -> str:
        timestamp = "2026-02-11T23:59:00"

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        action_str = str(action).strip().lower()
        valid_actions = ["add", "remove"]
        if action_str not in valid_actions:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid action '{action_str}'. Valid values: {', '.join(valid_actions)}",
                }
            )

        pid = str(project_id).strip()
        uid = str(user_id).strip()

        projects = data.get("projects", {})
        users = data.get("users", {})
        project_members = data.get("project_members", {})
        work_items = data.get("work_items", {})

        if action_str == "add":
            project = projects.get(pid)
            if project is None:
                return json.dumps(
                    {"success": False, "error": f"Project '{pid}' not found"}
                )
            if str(project.get("status", "")) not in ["open", "in_progress"]:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Project '{pid}' is not active. Current status: {str(project.get('status', ''))}",
                    }
                )

            user = users.get(uid)
            if user is None:
                return json.dumps(
                    {"success": False, "error": f"User '{uid}' not found"}
                )
            if str(user.get("status", "")) != "active":
                return json.dumps(
                    {
                        "success": False,
                        "error": f"User '{uid}' is not active. Current status: {str(user.get('status', ''))}",
                    }
                )

            for pm in project_members.values():
                if str(pm.get("project_id", "")) == pid and str(pm.get("user_id", "")) == uid:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"User '{uid}' is already a member of project '{pid}'",
                        }
                    )

            if project_members:
                max_id = max(int(k) for k in project_members.keys())
                new_id = str(max_id + 1)
            else:
                new_id = "1"

            new_member = {
                "project_member_id": new_id,
                "user_id": uid,
                "project_id": pid,
                "joined_at": timestamp,
            }

            project_members[new_id] = new_member

            response = {
                "user_id": str(new_member.get("user_id", "")),
                "project_id": str(new_member.get("project_id", "")),
            }
            return json.dumps({"success": True, "project_member": response})

        elif action_str == "remove":
            # Validate project and user exist before checking membership
            project = projects.get(pid)
            if project is None:
                return json.dumps(
                    {"success": False, "error": f"Project '{pid}' not found"}
                )

            user = users.get(uid)
            if user is None:
                return json.dumps(
                    {"success": False, "error": f"User '{uid}' not found"}
                )

            target_key = None
            for key, pm in project_members.items():
                if str(pm.get("project_id", "")) == pid and str(pm.get("user_id", "")) == uid:
                    target_key = key
                    break

            if target_key is None:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"User '{uid}' is not a member of project '{pid}'",
                    }
                )

            # Check for assigned work items with open statuses
            for wi in work_items.values():
                if (str(wi.get("project_id", "")) == pid
                        and wi.get("assignee_user_id") is not None
                        and str(wi.get("assignee_user_id", "")) == uid):
                    wi_status = str(wi.get("status", ""))
                    if wi_status in ["open", "in_progress"]:
                        return json.dumps(
                            {
                                "success": False,
                                "error": f"Cannot remove: user '{uid}' has assigned issues with status '{wi_status}' in project '{pid}'",
                            }
                        )

            project_members.pop(target_key)

            username = str(user.get("username", "")) if user else uid
            project_name = str(project.get("project_name", "")) if project else pid

            return json.dumps(
                {
                    "success": True,
                    "message": f"User '{username}' has been removed from project '{project_name}'",
                }
            )

        return json.dumps({"success": False, "error": "Unexpected error"})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "manage_project_members",
                "description": "Manages project membership by adding or removing users.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "The action to perform",
                            "enum": ["add", "remove"],
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User identifier (user_id).",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier (project_id).",
                        },
                    },
                    "required": ["action", "user_id", "project_id"],
                },
            },
        }
