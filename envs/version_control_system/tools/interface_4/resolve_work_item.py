import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool
import base64


class ResolveWorkItem(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], project_id: str, auth_token: str) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        access_tokens = data.get("access_tokens", {})
        projects = data.get("projects", {})
        project_members = data.get("project_members", {})
        repositories = data.get("repositories", {})
        issues = data.get("issues", {})

        def encode(text: str) -> str:
            text_bytes = text.encode("utf-8")
            encoded_bytes = base64.b64encode(text_bytes)
            return encoded_bytes.decode("utf-8")

        # --- Authenticate user ---
        encoded_token = encode(auth_token)
        token_info = next(
            (
                info
                for info in access_tokens.values()
                if info.get("token_encoded") == encoded_token
            ),
            None,
        )

        if not token_info:
            return json.dumps(
                {"success": False, "error": "Invalid authentication token"}
            )
        user_id = token_info.get("user_id")

        # --- Validate project ---
        project = projects.get(project_id)
        membership = next(
            (
                m
                for m in project_members.values()
                if m["user_id"] == user_id and m["project_id"] == project_id
            ),
            None,
        )
        if not project:
            return json.dumps(
                {"success": False, "error": f"Project with id {project_id} not found"}
            )
        if not membership:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User access restricted. User is not a member of the specified project",
                }
            )

        # --- Fetch repositories under project ---
        project_repositories = [
            repo
            for repo in repositories.values()
            if repo.get("project_id") == project_id
        ]

        if not project_repositories:
            return json.dumps({"success": True, "work_items": []})

        repo_ids = {repo["repository_id"] for repo in project_repositories}

        # --- Fetch issues (work items) for those repositories ---
        work_items = [
            issue for issue in issues.values() if issue.get("repository_id") in repo_ids
        ]
        work_items_copy = []

        for item in work_items:
            item_copy = {**item}
            item_copy["work_item_id"] = item["issue_id"]
            work_items_copy.append(item_copy)

        return json.dumps(
            {
                "success": True,
                "project": {
                    "project_id": project_id,
                    "project_name": project.get("project_name"),
                },
                "work_items": work_items_copy,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "resolve_work_item",
                "description": (
                    "Resolves and retrieves all work items associated with a given project. "
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": (
                                "The unique identifier of the project whose work items should be retrieved."
                            ),
                        },
                        "auth_token": {
                            "type": "string",
                            "description": (
                                "Authentication token used to validate the requesting user."
                            ),
                        },
                    },
                    "required": ["project_id", "auth_token"],
                },
            },
        }
