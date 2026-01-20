import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class CreateNotification(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_id: str,
        notification_type: str,
        reference_type: str,
        reference_id: str,
        repo_id: str,
    ) -> str:

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        notifications = data.get("notifications", {})
        users = data.get("users", {})
        repositories = data.get("repositories", {})
        pull_requests = data.get("pull_requests", {})
        issues = data.get("issues", {})

        # Validate required fields
        if not user_id:
            return json.dumps({"success": False, "error": "Missing required parameter: user_id"})

        if not notification_type:
            return json.dumps({"success": False, "error": "Missing required parameter: notification_type"})

        if not reference_type:
            return json.dumps({"success": False, "error": "Missing required parameter: reference_type"})

        if not reference_id:
            return json.dumps({"success": False, "error": "Missing required parameter: reference_id"})

        if not repo_id:
            return json.dumps({"success": False, "error": "Missing required parameter: repo_id"})

        # Normalize inputs
        user_id = str(user_id).strip()
        notification_type = notification_type.strip().lower(
        ) if isinstance(notification_type, str) else ""
        reference_type = reference_type.strip().lower(
        ) if isinstance(reference_type, str) else ""
        reference_id = str(reference_id).strip()
        repo_id = str(repo_id).strip()

        # Validate user exists and is active
        if user_id not in users:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{user_id}' not found"
            })

        user = users[user_id]

        if user.get("status") != "active":
            return json.dumps({
                "success": False,
                "error": f"User '{user_id}' is not active"
            })

        # Validate repository exists
        repo = None
        for r_id, r in repositories.items():
            if str(r.get("repository_id")) == repo_id:
                repo = r
                break

        if not repo:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repo_id}' not found"
            })

        # Validate reference_type
        allowed_reference_types = {"pull_request", "issue"}
        if reference_type not in allowed_reference_types:
            return json.dumps({
                "success": False,
                "error": f"reference_type must be one of: {', '.join(sorted(allowed_reference_types))}"
            })

        # Validate notification_type
        allowed_notification_types = {
            "review_request", "pr_merged", "issue_assigned"}
        if notification_type not in allowed_notification_types:
            return json.dumps({
                "success": False,
                "error": f"notification_type must be one of: {', '.join(sorted(allowed_notification_types))}"
            })

        # Validate reference exists and belongs to the repository
        if reference_type == "pull_request":
            pr = None
            for pr_id, pr_record in pull_requests.items():
                if str(pr_record.get("pull_request_id")) == reference_id:
                    if str(pr_record.get("repository_id")) == repo_id:
                        pr = pr_record
                        break
                    else:
                        return json.dumps({
                            "success": False,
                            "error": f"Pull request '{reference_id}' does not belong to repository '{repo_id}'"
                        })

            if not pr:
                return json.dumps({
                    "success": False,
                    "error": f"Pull request with ID '{reference_id}' not found in repository '{repo_id}'"
                })

            # Validate notification_type matches reference_type
            if notification_type not in {"review_request", "pr_merged"}:
                return json.dumps({
                    "success": False,
                    "error": f"notification_type '{notification_type}' is not valid for reference_type 'pull_request'"
                })

        elif reference_type == "issue":
            issue = None
            for issue_id, issue_record in issues.items():
                if str(issue_record.get("issue_id")) == reference_id:
                    if str(issue_record.get("repository_id")) == repo_id:
                        issue = issue_record
                        break
                    else:
                        return json.dumps({
                            "success": False,
                            "error": f"Issue '{reference_id}' does not belong to repository '{repo_id}'"
                        })

            if not issue:
                return json.dumps({
                    "success": False,
                    "error": f"Issue with ID '{reference_id}' not found in repository '{repo_id}'"
                })

            # Validate notification_type matches reference_type
            if notification_type != "issue_assigned":
                return json.dumps({
                    "success": False,
                    "error": f"notification_type '{notification_type}' is not valid for reference_type 'issue'"
                })

        # Generate new notification ID
        new_notification_id = generate_id(notifications)

        # Set timestamp for created_at
        timestamp = "2026-01-01T23:59:00"

        # Create new notification record
        new_notification = {
            "notification_id": new_notification_id,
            "user_id": user_id,
            "notification_type": notification_type,
            "reference_type": reference_type,
            "reference_id": reference_id,
            "repository_id": repo_id,
            "is_read": False,
            "read_at": None,
            "created_at": timestamp,
        }

        # Add the new notification to the notifications dictionary
        notifications[new_notification_id] = new_notification

        return json.dumps({
            "success": True,
            "message": f"Notification created successfully for user '{user_id}'",
            "notification_id": new_notification_id,
            "notification_data": new_notification
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_notification",
                "description": "Creates a notification for a user about a pull request or issue.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user to notify.",
                        },
                        "notification_type": {
                            "type": "string",
                            "description": "The type of notification.",
                            "enum": ["review_request", "pr_merged", "issue_assigned"]
                        },
                        "reference_type": {
                            "type": "string",
                            "description": "The type of reference.",
                            "enum": ["pull_request", "issue"]
                        },
                        "reference_id": {
                            "type": "string",
                            "description": "The ID of the referenced pull request or issue.",
                        },
                        "repo_id": {
                            "type": "string",
                            "description": "The ID of the repository.",
                        },
                    },
                    "required": ["user_id", "notification_type", "reference_type", "reference_id", "repo_id"],
                },
            },
        }
