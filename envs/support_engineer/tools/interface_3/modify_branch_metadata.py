import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class ModifyBranchMetadata(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        branch_name: str,
        ticket_number: str,
    ) -> str:
        if not branch_name:
            return json.dumps({"error": "branch_name is required"})

        if not ticket_number:
            return json.dumps({"error": "ticket_number is required"})

        branches = data.get("branches", {})
        tickets = data.get("tickets", {})
        timestamp = "2026-02-02 23:59:00"

        branch_details = None
        for branch in branches.values():
            if branch.get("branch_name") == str(branch_name):
                branch_details = branch
                break

        if not branch_details:
            return json.dumps({"error": f"Branch '{branch_name}' not found"})

        ticket_id = None
        for t_id, ticket in tickets.items():
            if ticket.get("ticket_number") == str(ticket_number):
                ticket_id = t_id
                break

        if not ticket_id:
            return json.dumps({"error": f"Ticket with number '{ticket_number}' not found"})

        branch_details["linked_ticket_id"] = str(ticket_id)
        branch_details["updated_at"] = timestamp

        return json.dumps({
            "success": True,
            "branch": {
                "branch_id": str(branch_details["branch_id"]),
                "repository_id": str(branch_details["repository_id"]),
                "branch_name": str(branch_details["branch_name"]),
                "source_branch_name": str(branch_details["source_branch_name"]) if branch_details.get("source_branch_name") else None,
                "commit_sha": str(branch_details["commit_sha"]) if branch_details.get("commit_sha") else None,
                "linked_ticket_id": str(branch_details["linked_ticket_id"]),
                "created_by": str(branch_details["created_by"]) if branch_details.get("created_by") else None,
                "created_at": str(branch_details["created_at"]),
                "updated_at": str(branch_details["updated_at"]),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "modify_branch_metadata",
                "description": "Updates the metadata of a branch by linking it to a specific ticket. It should be used when you need to associate a branch with a ticket.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "branch_name": {
                            "type": "string",
                            "description": "The name of the branch",
                        },
                        "ticket_number": {
                            "type": "string",
                            "description": "The ticket number to link to the branch",
                        },
                    },
                    "required": ["branch_name", "ticket_number"],
                },
            },
        }
