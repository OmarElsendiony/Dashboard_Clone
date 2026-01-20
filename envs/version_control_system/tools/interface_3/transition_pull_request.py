import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class TransitionPullRequest(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        pull_request_id: str,
        action: str,
        merged_by: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not pull_request_id:
            return json.dumps({"success": False, "error": "pull_request_id is required to transition pull request"})
        if not action:
            return json.dumps({"success": False, "error": "action is required to transition pull request"})

        # Validate action
        valid_actions = ["close", "merge", "reopen", "convert_to_draft"]
        if action not in valid_actions:
            return json.dumps({"success": False, "error": f"Invalid action '{action}'. Valid values: close, merge, reopen, convert_to_draft"})

        # Validate merged_by is required for merge action
        if action == "merge" and not merged_by:
            return json.dumps({"success": False, "error": "merged_by is required when action is 'merge'"})

        pull_requests = data.get("pull_requests", {})
        users = data.get("users", {})

        # Validate pull request exists
        if str(pull_request_id) not in pull_requests:
            return json.dumps({"success": False, "error": f"Pull request with id '{pull_request_id}' not found"})

        pull_request = pull_requests[str(pull_request_id)]
        current_status = pull_request.get("status")

        # Validate merged_by user exists if provided
        if merged_by is not None:
            if str(merged_by) not in users:
                return json.dumps({"success": False, "error": f"User with id '{merged_by}' not found"})

        # Validate state transitions
        if action == "close":
            if current_status == "closed":
                return json.dumps({"success": False, "error": "Pull request is already closed"})
            if current_status == "merged":
                return json.dumps({"success": False, "error": "Cannot close a merged pull request"})
            pull_request["status"] = "closed"
            pull_request["closed_at"] = "2026-01-01T23:59:00"

        elif action == "merge":
            if current_status == "merged":
                return json.dumps({"success": False, "error": "Pull request is already merged"})
            if current_status == "closed":
                return json.dumps({"success": False, "error": "Cannot merge a closed pull request"})
            if current_status == "draft":
                return json.dumps({"success": False, "error": "Cannot merge a draft pull request"})
            pull_request["status"] = "merged"
            pull_request["merged_at"] = "2026-01-01T23:59:00"
            pull_request["merged_by"] = merged_by

        elif action == "reopen":
            if current_status != "closed":
                return json.dumps({"success": False, "error": "Can only reopen a closed pull request"})
            pull_request["status"] = "open"
            pull_request["closed_at"] = None

        elif action == "convert_to_draft":
            if current_status != "open":
                return json.dumps({"success": False, "error": "Can only convert an open pull request to draft"})
            pull_request["status"] = "draft"

        pull_request["updated_at"] = "2026-01-01T23:59:00"

        return json.dumps({"success": True, "result": pull_request})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "transition_pull_request",
                "description": "Transitions a pull request to a new status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pull_request_id": {
                            "type": "string",
                            "description": "The unique identifier of the pull request to transition."
                        },
                        "action": {
                            "type": "string",
                            "description": "The action to perform. Valid values: close, merge, reopen, convert_to_draft."
                        },
                        "merged_by": {
                            "type": "string",
                            "description": "The unique identifier of the user who is merging the pull request. Required when action is 'merge'."
                        }
                    },
                    "required": ["pull_request_id", "action"]
                }
            }
        }
