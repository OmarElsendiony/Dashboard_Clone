import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class UpdatePullRequest(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        pull_request_id: str,
        updates: Dict[str, Any],
    ) -> str:
        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        if not pull_request_id:
            return json.dumps({"success": False, "error": "Pull request ID is required"})

        if not updates:
            return json.dumps({"success": False, "error": "At least one update field is required"})

        if not isinstance(updates, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'updates' must be a dict"})

        pull_requests = data.get("pull_requests", {})
        # Validate pull request existence
        if pull_request_id not in pull_requests:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Pull request with ID '{pull_request_id}' does not exist",
                }
            )
        pull_request = pull_requests[pull_request_id]
        # Valid fields that can be updated
        valid_update_fields = {
            "title",
            "description",
            "status",
            "assigned_team_lead",
            "gate_ci_status",
            "is_emergency_fix",
        }
        # Apply updates
        for field, value in updates.items():
            if field in valid_update_fields:
                # validate enums
                if field == "status":
                    if value not in ["open", "closed", "merged", "draft"]:
                        return json.dumps(
                            {
                                "success": False,
                                "error": f"Invalid status value '{value}', must be one of ['open', 'closed', 'merged', 'draft']",
                            }
                        )
                if field == "gate_ci_status":
                    if value not in ["Pending", "Success", "Failure"]:
                        return json.dumps(
                            {
                                "success": False,
                                "error": f"Invalid gate_ci_status value '{value}', must be one of ['Pending', 'Success', 'Failure']",
                            }
                        )
                if field == "assigned_team_lead":
                    users = data.get("users", {})
                    if value not in users:
                        return json.dumps(
                            {
                                "success": False,
                                "error": f"User with ID '{value}' does not exist to be assigned as team lead",
                            }
                        )
                pull_request[field] = value
        pull_request["updated_at"] = "2026-02-02 23:59:00"  # example timestamp
        pull_requests[pull_request_id] = pull_request
        return json.dumps(
            {
                "success": True,
                "pull_request": pull_request,
            }
        )


    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_pull_request",
                "description": "Modifies the details of an existing pull request. Use when updating a pull request metadata, including the title, description, and assignment of a team lead. Also allows updating the status and CI gate information to reflect the current state of the review process.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pull_request_id": {
                            "type": "string",
                            "description": "The ID of the pull request to be updated.",
                        },
                        "updates": {
                            "type": "object",
                            "description": "A dictionary of fields to update on the pull request.",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "The new title of the pull request.",
                                },
                                "description": {
                                    "type": "string",
                                    "description": "The new description of the pull request.",
                                },
                                "status": {
                                    "type": "string",
                                    "description": "The new status of the pull request.",
                                    "enum": ["open", "closed", "merged", "draft"]
                                },
                                "assigned_team_lead": {
                                    "type": "string",
                                    "description": "The ID of the team lead assigned to the pull request.",
                                },
                                "gate_ci_status": {
                                    "type": "string",
                                    "description": "The CI status of the pull request.",
                                    "enum": ["Pending", "Success", "Failure"]
                                },
                                "is_emergency_fix": {
                                    "type": "boolean",
                                    "description": "Whether the pull request is an emergency fix.",
                                }
                            },
                    },
                    },
                    "required": ["pull_request_id", "updates"],
                },
            },
        }
