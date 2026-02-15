import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateNewIssue(Tool):
    @staticmethod
    def invoke(
            data: Dict[str, Any],
            repository_id: str,
            title: str,
            description: str,
            issue_type: str = "incident",
            ticket_id: Optional[str] = None,
        ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        issues = data.get("issues", {})
        def generate_id(table: Dict[str, Any]) -> str:
            return str(max([int(k) for k in table.keys()], default=0) + 1)
        # validate the repository_id
        repositories = data.get("repositories", {})
        if repository_id not in repositories:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repository_id}' does not exist"
            })
        # validate the ticket_id if provided
        tickets = data.get("tickets", {})
        if ticket_id and ticket_id not in tickets:
            return json.dumps({
                "success": False,
                "error": f"Ticket with ID '{ticket_id}' does not exist"
            })
        # validate issue_type
        valid_issue_types = ['bug', 'configuration', 'incident', 'feature']
        if issue_type not in valid_issue_types:
            return json.dumps({
                "success": False,
                "error": f"Invalid issue_type. Must be one of {valid_issue_types}"
            })
        new_issue_id = generate_id(issues)
        new_issue = {
            "issue_id": new_issue_id,
            "repository_id": str(repository_id),
            "originating_ticket_id": str(ticket_id) if ticket_id else None,
            "title": str(title),
            "description": str(description),
            "type": str(issue_type),
            "status": "Open",
            "reproduction_verified": False,
            "reproduction_env": None,
            "created_at": "2026-02-02 23:59:00",
            "updated_at": "2026-02-02 23:59:00"
        }
        issues[new_issue_id] = new_issue
        data["issues"] = issues
        return json.dumps({"success": True, "issue": new_issue})
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_new_issue",
                "description": "Creates a new issue in a specified repository. Use to log bugs, feature requests, or incidents related to the repository. Optionally links the issue to an originating support ticket.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The ID of the repository where the issue is being created."
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the new issue."
                        },
                        "description": {
                            "type": "string",
                            "description": "The description of the new issue."
                        },
                        "ticket_id": {
                            "type": "string",
                            "description": "The ID of the originating ticket, (Optional)."
                        },
                        "issue_type": {
                            "type": "string",
                            "description": "The type of the issue.",
                            "enum": ["bug", "configuration", "incident", "feature"]
                        }
                    },
                    "required": ["repository_id", "title", "description"]
                }
            }
        }
