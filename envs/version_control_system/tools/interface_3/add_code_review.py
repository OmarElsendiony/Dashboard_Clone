import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class AddCodeReview(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        action: str,
        pull_request_id: Optional[str] = None,
        reviewer_id: Optional[str] = None,
        file_path: Optional[str] = None,
        body: Optional[str] = None,
        review_type: Optional[str] = None,
        status: Optional[str] = None,
        code_review_id: Optional[str] = None
    ) -> str:
        """
        Creates or updates a code review entry on a pull request.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not action:
            return json.dumps({"success": False, "error": "action is required"})

        # Validate action
        valid_actions = ["create", "update"]
        if action not in valid_actions:
            return json.dumps({"success": False, "error": f"Invalid action '{action}'. Valid values: create, update"})

        pull_requests = data.get("pull_requests", {})
        users = data.get("users", {})
        code_reviews = data.get("code_reviews", {})

        # Validate status
        valid_statuses = ["pending", "resolved", "outdated"]
        if status is not None and status not in valid_statuses:
            return json.dumps({"success": False, "error": f"Invalid status '{status}'. Valid values: pending, resolved, outdated"})

        if action == "create":
            # Validate required fields for create
            if not pull_request_id:
                return json.dumps({"success": False, "error": "pull_request_id is required for create action"})
            if not reviewer_id:
                return json.dumps({"success": False, "error": "reviewer_id is required for create action"})
            if not file_path:
                return json.dumps({"success": False, "error": "file_path is required for create action"})
            if not body:
                return json.dumps({"success": False, "error": "body is required for create action"})
            if not review_type:
                return json.dumps({"success": False, "error": "review_type is required for create action"})
            if not status:
                return json.dumps({"success": False, "error": "status is required for create action"})

            # Validate review_type
            valid_review_types = ["comment", "suggestion", "question"]
            if review_type not in valid_review_types:
                return json.dumps({"success": False, "error": f"Invalid review_type '{review_type}'. Valid values: comment, suggestion, question"})

            # Validate pull request exists
            if str(pull_request_id) not in pull_requests:
                return json.dumps({"success": False, "error": f"Pull request with id '{pull_request_id}' not found"})

            pull_request = pull_requests[str(pull_request_id)]

            # Validate pull request is open or draft
            pr_status = pull_request.get("status")
            if pr_status in ["closed", "merged"]:
                return json.dumps({"success": False, "error": f"Cannot add code review on a {pr_status} pull request"})

            # Validate reviewer exists
            if str(reviewer_id) not in users:
                return json.dumps({"success": False, "error": f"User with id '{reviewer_id}' not found"})

            # Generate new code_review_id
            if code_reviews:
                max_id = max(int(k) for k in code_reviews.keys())
                new_id = str(max_id + 1)
            else:
                new_id = "1"

            # Create code review record
            new_code_review = {
                "code_review_id": new_id,
                "pull_request_id": pull_request_id,
                "reviewer_id": reviewer_id,
                "file_path": file_path,
                "comment_body": body,
                "review_type": review_type,
                "status": status,
                "created_at": "2026-01-01T23:59:00",
                "updated_at": "2026-01-01T23:59:00"
            }

            code_reviews[new_id] = new_code_review

            return json.dumps({"success": True, "result": new_code_review})

        elif action == "update":
            # Validate required fields for update
            if not code_review_id:
                return json.dumps({"success": False, "error": "code_review_id is required for update action"})
            if not status:
                return json.dumps({"success": False, "error": "status is required for update action"})

            # Validate code review exists
            if str(code_review_id) not in code_reviews:
                return json.dumps({"success": False, "error": f"Code review with id '{code_review_id}' not found"})

            code_review = code_reviews[str(code_review_id)]
            code_review["status"] = status
            code_review["updated_at"] = "2026-01-01T23:59:00"

            return json.dumps({"success": True, "result": code_review})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_code_review",
                "description": "Creates or updates a code review entry on a pull request. Use action 'create' to add a new code review comment on a specific file. Use action 'update' to change the status of an existing code review.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "The action to perform. Valid values: create, update."
                        },
                        "pull_request_id": {
                            "type": "string",
                            "description": "The unique identifier of the pull request. Required for create action."
                        },
                        "reviewer_id": {
                            "type": "string",
                            "description": "The unique identifier of the user adding the code review. Required for create action."
                        },
                        "file_path": {
                            "type": "string",
                            "description": "The path of the file being reviewed. Required for create action."
                        },
                        "body": {
                            "type": "string",
                            "description": "The content of the code review comment. Required for create action."
                        },
                        "review_type": {
                            "type": "string",
                            "description": "The type of code review. Valid values: comment, suggestion, question. Required for create action."
                        },
                        "status": {
                            "type": "string",
                            "description": "The status for the code review. Valid values: pending, resolved, outdated. Required for both create and update actions."
                        },
                        "code_review_id": {
                            "type": "string",
                            "description": "The unique identifier of the code review to update. Required for update action."
                        }
                    },
                    "required": ["action"]
                }
            }
        }
