import json
from typing import Dict, Optional
from tau_bench.envs.tool import Tool


class UpdateIssues(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, object],
        issue_id: str,
        ticket_id: Optional[str] = None,
        status: Optional[str] = None,
        description: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format for issues"}
            )

        if not issue_id:
            return json.dumps({"success": False, "error": "issue_id is required"})

        issues = data.get("issues", {})
        tickets = data.get("tickets", {})

        if issue_id not in issues:
            return json.dumps(
                {"success": False, "error": f"Issue with ID {issue_id} not found"}
            )

        if ticket_id:
            if ticket_id not in tickets:
                return json.dumps(
                    {"success": False, "error": f"Ticket with ID {ticket_id} not found"}
                )

        valid_statuses = ["Open", "In_Progress", "Resolved"]
        if status and status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}",
                }
            )

        issue = issues[issue_id].copy()

        if ticket_id is not None:
            issue["originating_ticket_id"] = ticket_id
        if status is not None:
            issue["status"] = status
        if description is not None:
            issue["description"] = description

        issue["updated_at"] = "2026-02-02 23:59:00"

        issues[issue_id] = issue

        return json.dumps(
            {
                "success": True,
                "issue": issue,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, object]:
        return {
            "type": "function",
            "function": {
                "name": "update_issues",
                "description": "Update an existing issue to link it to a ticket or modify its status/description. Use this to link a matching issue to a ticket using originating_ticket_id, or to update issue status and description. issue_id is required. Optionally update ticket_id to link the issue to a ticket, status to change issue state, or description to update issue details.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "issue_id": {
                            "type": "string",
                            "description": "ID of the issue to update (required)",
                        },
                        "ticket_id": {
                            "type": "string",
                            "description": "Ticket ID to link to this issue (sets originating_ticket_id) (optional)",
                        },
                        "status": {
                            "type": "string",
                            "description": "Update issue status. Allowed values: 'Open', 'In_Progress', 'Resolved' (optional)",
                            "enum": ["Open", "In_Progress", "Resolved"],
                        },
                        "description": {
                            "type": "string",
                            "description": "Update issue description (optional)",
                        },
                    },
                    "required": ["issue_id"],
                },
            },
        }
