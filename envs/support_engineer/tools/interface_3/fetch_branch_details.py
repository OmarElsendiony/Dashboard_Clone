import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class FetchBranchDetails(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_name: str,
        branch_name: str,
    ) -> str:
        if not repository_name:
            return json.dumps({"error": "repository_name is required"})

        if not branch_name:
            return json.dumps({"error": "branch_name is required"})

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})
        tickets = data.get("tickets", {})

        repository_id = None
        for r_id, repo in repositories.items():
            if repo.get("repository_name") == str(repository_name):
                repository_id = r_id
                break

        if not repository_id:
            return json.dumps({"error": f"Repository with name '{repository_name}' not found"})

        branch_details = None
        for branch in branches.values():
            if (
                branch.get("branch_name") == str(branch_name) and
                str(branch.get("repository_id")) == str(repository_id)
            ):
                branch_details = branch
                break

        if not branch_details:
            return json.dumps(
                {"error": f"Branch '{branch_name}' not found in repository '{repository_name}'"}
            )

        linked_ticket_id = branch_details.get("linked_ticket_id")
        linked_ticket_number = None
        if linked_ticket_id:
            ticket = tickets.get(str(linked_ticket_id))
            if ticket:
                linked_ticket_number = ticket.get("ticket_number")

        return json.dumps({
            "success": True,
            "branch": {
                "branch_id": str(branch_details["branch_id"]),
                "repository_id": str(branch_details["repository_id"]),
                "branch_name": str(branch_details["branch_name"]),
                "source_branch_name": str(branch_details["source_branch_name"]) if branch_details.get("source_branch_name") else None,
                "commit_sha": str(branch_details["commit_sha"]) if branch_details.get("commit_sha") else None,
                "linked_ticket_id": str(linked_ticket_id) if linked_ticket_id else None,
                "linked_ticket_number": str(linked_ticket_number) if linked_ticket_number else None,
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
                "name": "fetch_branch_details",
                "description": "Fetches details of a branch in a repository. It should be used when you need to retrieve information about a specific branch.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_name": {
                            "type": "string",
                            "description": "The name of the repository",
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "The name of the branch",
                        },
                    },
                    "required": ["repository_name", "branch_name"],
                },
            },
        }
