import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class MergePullRequest(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        pull_request_id: str,
        merged_by: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not pull_request_id:
            return json.dumps(
                {"success": False, "error": "pull_request_id is required"}
            )

        if not merged_by:
            return json.dumps({"success": False, "error": "merged_by is required"})

        pull_requests = data.get("pull_requests", {})
        users = data.get("users", {})
        tickets = data.get("tickets", {})

        if str(pull_request_id) not in pull_requests:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Pull request with id '{pull_request_id}' not found",
                }
            )

        pull_request = pull_requests[str(pull_request_id)]

        if pull_request.get("status") != "open":
            return json.dumps(
                {
                    "success": False,
                    "error": f"Pull request '{pull_request_id}' is not open. Current status: {pull_request.get('status')}",
                }
            )

        if str(merged_by) not in users:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with id '{merged_by}' not found",
                }
            )

        user = users[str(merged_by)]
        if user.get("status") != "active":
            return json.dumps(
                {
                    "success": False,
                    "error": f"User '{merged_by}' is not active. Current status: {user.get('status')}",
                }
            )

        linked_ticket_id = pull_request.get("linked_ticket_id")
        if linked_ticket_id is None:
            return json.dumps(
                {
                    "success": False,
                    "error": "Merge is blocked: pull request must be linked to a ticket ",
                }
            )

        if str(linked_ticket_id) not in tickets:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Linked ticket '{linked_ticket_id}' not found",
                }
            )

        ticket = tickets[str(linked_ticket_id)]
        valid_ticket_statuses = ["open", "pending", "in_progress"]
        if ticket.get("status") not in valid_ticket_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Linked ticket '{linked_ticket_id}' is not in valid state for merge. Must be one of: {', '.join(valid_ticket_statuses)}. Current status: {ticket.get('status')}",
                }
            )

        static_timestamp = "2026-02-02 23:59:00"

        pull_request["status"] = "merged"
        pull_request["merged_by"] = merged_by
        pull_request["merged_at"] = static_timestamp
        pull_request["updated_at"] = static_timestamp

        _PR_RESPONSE_KEYS = (
            "pull_request_id",
            "repository_id",
            "pull_request_number",
            "title",
            "source_branch_name",
            "author_id",
            "target_branch_name",
            "status",
            "linked_ticket_id",
            "created_at",
            "updated_at",
            "assigned_team_lead",
            "merged_by",
            "merged_at",
            "closed_at",
        )
        pull_request_response = {
            k: pull_request.get(k) for k in _PR_RESPONSE_KEYS
        }
        return json.dumps({"success": True, "pull_request": pull_request_response})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "merge_pull_request",
                "description": "Merge an open pull request into its target branch.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pull_request_id": {
                            "type": "string",
                            "description": "Pull request identifier to merge",
                        },
                        "merged_by": {
                            "type": "string",
                            "description": "User identifier performing the merge",
                        },
                    },
                    "required": ["pull_request_id", "merged_by"],
                },
            },
        }
