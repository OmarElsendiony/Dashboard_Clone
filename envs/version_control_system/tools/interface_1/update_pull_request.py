import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpdatePullRequest(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        access_token: str,
        pull_request_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        merged_by: Optional[str] = None
    ) -> str:
        timestamp = "2026-01-01T23:59:00"

        try:
            encoded_input_token = base64.b64encode(access_token.encode('utf-8')).decode('utf-8')
        except Exception:
            return json.dumps({"error": "Failed to process access token"})

        tokens = data.get("access_tokens", {})
        valid_token = False
        for token in tokens.values():
            if token.get("token_encoded") == encoded_input_token and token.get("status") == "active":
                if token.get("expires_at") > timestamp:
                    valid_token = True
                    break

        if not valid_token:
            return json.dumps({"error": "Invalid or expired access token"})

        pull_requests = data.get("pull_requests", {})
        users = data.get("users", {})

        if pull_request_id not in pull_requests:
            return json.dumps({"error": f"Pull request with ID {pull_request_id} not found"})

        pr = pull_requests[pull_request_id]

        valid_statuses = ['open', 'closed', 'merged', 'draft']
        if status and status not in valid_statuses:
            return json.dumps({"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"})

        if status == 'merged':
            if not merged_by:
                if not pr.get("merged_by"):
                    return json.dumps({"error": "merged_by user_id is required when setting status to merged"})
            else:
                if merged_by not in users:
                    return json.dumps({"error": f"User {merged_by} (merged_by) not found"})

        if title is not None:
            pr["title"] = title
        if description is not None:
            pr["description"] = description

        if status is not None:
            if status == 'merged':
                pr["merged_at"] = timestamp
                pr["closed_at"] = timestamp
                if merged_by:
                    pr["merged_by"] = merged_by
            elif status == 'closed':
                pr["closed_at"] = timestamp
                pr["merged_at"] = None
                pr["merged_by"] = None
            elif status == 'open':
                pr["closed_at"] = None
                pr["merged_at"] = None
                pr["merged_by"] = None

            pr["status"] = status

        pr["updated_at"] = timestamp
        pull_requests[pull_request_id] = pr

        return json.dumps(pr)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_pull_request",
                "description": "Updates details of an existing pull request, such as title, description, or status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "access_token": {
                            "type": "string",
                            "description": "The access token for authentication."
                        },
                        "pull_request_id": {
                            "type": "string",
                            "description": "The unique identifier of the pull request."
                        },
                        "title": {
                            "type": "string",
                            "description": "The new title of the pull request."
                        },
                        "description": {
                            "type": "string",
                            "description": "The new description of the pull request."
                        },
                        "status": {
                            "type": "string",
                            "description": "The new status of the pull request. Allowed values: 'open', 'closed', 'merged', 'draft'."
                        },
                        "merged_by": {
                            "type": "string",
                            "description": "The user ID of the person merging the pull request. Required if status is set to 'merged'."
                        }
                    },
                    "required": ["access_token", "pull_request_id"]
                }
            }
        }