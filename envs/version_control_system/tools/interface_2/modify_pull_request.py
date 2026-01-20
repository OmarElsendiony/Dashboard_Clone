import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ModifyPullRequest(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        pull_request_id: str,
        user_id: str,
        status: Optional[str] = None,
        target_branch: Optional[str] = None,
        description: Optional[str] = None,
        title: Optional[str] = None,
    ) -> str:
        timestamp = "2026-01-01T23:59:00"

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        # Check at least one update field is provided
        if not any([status, target_branch, description, title]):
            return json.dumps({
                "success": False,
                "error": "At least one of status, target_branch, description, or title must be provided for update",
            })

        pull_requests_dict = data.get("pull_requests", {})

        pull_request_id_str = str(pull_request_id).strip()
        user_id_str = str(user_id).strip()
        status_str = str(status).strip() if status else None
        target_branch_str = str(target_branch).strip() if target_branch else None
        description_str = str(description).strip() if description is not None else None
        title_str = str(title).strip() if title else None

        pull_request = pull_requests_dict[pull_request_id_str]

        if status_str:
            valid_statuses = ["open", "closed", "merged", "draft"]
            if status_str not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status '{status_str}'. Must be one of: {', '.join(valid_statuses)}",
                })
            pull_request["status"] = status_str
            
            if status_str == "closed":
                pull_request["closed_at"] = timestamp
            elif status_str == "merged":
                pull_request["merged_at"] = timestamp
                pull_request["merged_by"] = user_id_str

        if target_branch_str:
            pull_request["target_branch"] = target_branch_str

        if description_str is not None:
            pull_request["description"] = description_str

        if title_str:
            pull_request["title"] = title_str

        pull_request["updated_at"] = timestamp

        pull_request_return = pull_request.copy()
        pull_request_return["pull_request_id"] = pull_request_id_str

        return json.dumps({
            "success": True,
            "pull_request": pull_request_return,
            "message": f"Pull request '{pull_request_id_str}' updated successfully",
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "modify_pull_request",
                "description": "Modifies a pull request's details.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pull_request_id": {
                            "type": "string",
                            "description": "The ID of the pull request to modify.",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user performing the modification.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional. Accepted values are open, closed, merged, draft",
                        },
                        "target_branch": {
                            "type": "string",
                            "description": "Optional. The new target branch name.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional. The new description.",
                        },
                        "title": {
                            "type": "string",
                            "description": "Optional. The new title.",
                        },
                    },
                    "required": ["pull_request_id", "user_id"],
                },
            },
        }
