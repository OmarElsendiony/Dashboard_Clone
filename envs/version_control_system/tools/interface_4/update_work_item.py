import json
import base64
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class UpdateWorkItem(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        work_item_id: str,
        update_dict: Dict[str, Any],
        auth_token: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not isinstance(update_dict, dict) or not update_dict:
            return json.dumps(
                {"success": False, "error": "update_dict must be a non-empty object"}
            )

        access_tokens = data.get("access_tokens", {})
        repositories = data.get("repositories", {})
        repository_collaborators = data.get("repository_collaborators", {})
        issues = data.get("issues", {})

        def encode(text: str) -> str:
            return base64.b64encode(text.encode("utf-8")).decode("utf-8")

        # --- Authenticate requester ---
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

        requester_id = token_info.get("user_id")

        # --- Validate work item ---
        issue = issues.get(work_item_id)
        if not issue:
            return json.dumps({"success": False, "error": "Work item not found"})

        repository_id = issue.get("repository_id")
        repository = repositories.get(repository_id)
        if not repository:
            return json.dumps({"success": False, "error": "Repository not found"})

        # --- Authorization: write or admin ---
        permission = next(
            (
                c
                for c in repository_collaborators.values()
                if c.get("repository_id") == repository_id
                and c.get("user_id") == requester_id
                and c.get("permission_level") in {"write", "admin"}
            ),
            None,
        )

        if not permission:
            return json.dumps(
                {
                    "success": False,
                    "error": "Access denied. Write or admin permission required.",
                }
            )

        now = "2026-01-01T23:59:00"

        # --- Handle assignee update ---
        assignee_id = update_dict.get("assignee_id")
        if assignee_id:
            assignee_permission = next(
                (
                    c
                    for c in repository_collaborators.values()
                    if c.get("repository_id") == repository_id
                    and c.get("user_id") == assignee_id
                ),
                None,
            )

            if not assignee_permission:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Assignee is not a collaborator on the repository.",
                    }
                )

            issue["assignee_id"] = assignee_id

        # --- Allowed updates validation ---
        allowed_fields = {"title", "description", "status", "priority"}
        allowed_priority = {"low", "medium", "high", "critical"}
        allowed_status = {"open", "in_progress", "closed"}
        meta_fields = {"assignee_id", "comment"}

        for key in update_dict.keys():
            if key not in allowed_fields and key not in meta_fields:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Field '{key}' is not allowed to be updated",
                    }
                )

        # --- Apply field updates ---
        for key, value in update_dict.items():
            if key == "priority":
                if value not in allowed_priority:
                    return json.dumps(
                        {
                            "success": False,
                            "error": (
                                "Invalid priority level. "
                                "Accepted values: low, medium, high, critical."
                            ),
                        }
                    )
                issue["priority"] = value

            elif key == "status":
                if value not in allowed_status:
                    return json.dumps(
                        {
                            "success": False,
                            "error": (
                                "Invalid status value. "
                                "Accepted values: open, in_progress, closed."
                            ),
                        }
                    )
                issue["status"] = value

            elif key in {"title", "description"}:
                issue[key] = value

        # --- Status lifecycle handling ---
        if update_dict.get("status") == "closed":
            issue["closed_at"] = now
        elif "status" in update_dict:
            issue["closed_at"] = None

        issue["updated_at"] = now

        # --- Optional comment handling ---
        comment = update_dict.get("comment")
        if comment:
            comments = data.setdefault("comments", {})
            try:
                comment_id = str(max(int(k) for k in comments.keys()) + 1)
            except ValueError:
                comment_id = "1"

            comments[comment_id] = {
                "comment_id": comment_id,
                "commentable_type": "issue",
                "commentable_id": work_item_id,
                "author_id": requester_id,
                "comment_body": comment,
                "created_at": now,
                "updated_at": now,
            }

        # --- Output with naming consistency ---
        output_item = {**issue, "work_item_id": issue["issue_id"]}

        return json.dumps({"success": True, "work_item": output_item})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_work_item",
                "description": (
                    "Updates an existing work item (issue) in a repository. "
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "work_item_id": {
                            "type": "string",
                            "description": "ID of the work item to update.",
                        },
                        "update_dict": {
                            "type": "object",
                            "description": (
                                "Fields to update. "
                                "Allowed keys: 'title' (string), 'description' (string), "
                                "'status' (enum: ['open', 'in_progress', 'closed']), "
                                "'priority' (enum: ['low', 'medium', 'high', 'critical']), "
                                "'assignee_id' (string), 'comment' (string)."
                            ),
                        },
                        "auth_token": {
                            "type": "string",
                            "description": "Authentication token of the requesting user.",
                        },
                    },
                    "required": ["work_item_id", "update_dict", "auth_token"],
                },
            },
        }
