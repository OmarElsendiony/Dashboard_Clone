import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class DispatchNotification(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_id: str,
        notification_type: str,
        reference_type: str,
        reference_id: str,
        repository_id: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not user_id:
            return json.dumps({"success": False, "error": "user_id is required to dispatch a notification"})
        if not notification_type:
            return json.dumps({"success": False, "error": "notification_type is required to dispatch a notification"})
        if not reference_type:
            return json.dumps({"success": False, "error": "reference_type is required to dispatch a notification"})
        if not reference_id:
            return json.dumps({"success": False, "error": "reference_id is required to dispatch a notification"})

        # Validate notification_type
        valid_notification_types = ["mention", "review_request", "issue_assigned", "pr_merged", "ci_failed"]
        if notification_type not in valid_notification_types:
            return json.dumps({"success": False, "error": f"Invalid notification_type '{notification_type}'. Valid values: mention, review_request, issue_assigned, pr_merged, ci_failed"})

        # Validate reference_type
        valid_reference_types = ["issue", "pull_request", "commit", "release"]
        if reference_type not in valid_reference_types:
            return json.dumps({"success": False, "error": f"Invalid reference_type '{reference_type}'. Valid values: issue, pull_request, commit, release"})

        users = data.get("users", {})
        repositories = data.get("repositories", {})
        issues = data.get("issues", {})
        pull_requests = data.get("pull_requests", {})
        commits = data.get("commits", {})
        releases = data.get("releases", {})
        notifications = data.get("notifications", {})

        # Validate user exists
        if str(user_id) not in users:
            return json.dumps({"success": False, "error": f"User with id '{user_id}' not found"})

        # Validate repository exists if provided
        if repository_id is not None and str(repository_id) not in repositories:
            return json.dumps({"success": False, "error": f"Repository with id '{repository_id}' not found"})

        # Validate reference_id based on reference_type
        if reference_type == "issue":
            if str(reference_id) not in issues:
                return json.dumps({"success": False, "error": f"Issue with id '{reference_id}' not found"})
        elif reference_type == "pull_request":
            if str(reference_id) not in pull_requests:
                return json.dumps({"success": False, "error": f"Pull request with id '{reference_id}' not found"})
        elif reference_type == "commit":
            if str(reference_id) not in commits:
                return json.dumps({"success": False, "error": f"Commit with id '{reference_id}' not found"})
        elif reference_type == "release":
            if str(reference_id) not in releases:
                return json.dumps({"success": False, "error": f"Release with id '{reference_id}' not found"})

        # Generate new notification_id
        if notifications:
            max_id = max(int(k) for k in notifications.keys())
            new_notification_id = str(max_id + 1)
        else:
            new_notification_id = "1"

        # Create notification record
        new_notification = {
            "notification_id": new_notification_id,
            "user_id": user_id,
            "notification_type": notification_type,
            "reference_type": reference_type,
            "reference_id": reference_id,
            "repository_id": repository_id,
            "is_read": False,
            "read_at": None,
            "created_at": "2026-01-01T23:59:00"
        }

        notifications[new_notification_id] = new_notification

        return json.dumps({"success": True, "result": new_notification})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "dispatch_notification",
                "description": "Dispatches a notification to a user about an event related to an issue, pull request, commit, or release.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The unique identifier of the user to notify."
                        },
                        "notification_type": {
                            "type": "string",
                            "description": "The type of notification. Valid values: mention, review_request, issue_assigned, pr_merged, ci_failed."
                        },
                        "reference_type": {
                            "type": "string",
                            "description": "The type of entity the notification refers to. Valid values: issue, pull_request, commit, release."
                        },
                        "reference_id": {
                            "type": "string",
                            "description": "The unique identifier of the referenced entity (issue_id, pull_request_id, commit_id, or release_id)."
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository associated with the notification (optional)."
                        }
                    },
                    "required": ["user_id", "notification_type", "reference_type", "reference_id"]
                }
            }
        }
