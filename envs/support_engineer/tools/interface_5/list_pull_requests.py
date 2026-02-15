import json
from typing import Dict, Optional
from tau_bench.envs.tool import Tool


class ListPullRequests(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, object],
        repository_id: str,
        status: str,
        source_branch_name: Optional[str] = None,
        linked_ticket_id: Optional[str] = None,
        pull_request_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format for pull requests"}
            )

        if not repository_id:
            return json.dumps({"success": False, "error": "repository_id is required"})

        if not status:
            return json.dumps({"success": False, "error": "status is required"})

        if status not in ["open", "closed", "merged", "draft"]:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be 'open', 'closed', 'merged', or 'draft'",
                }
            )

        pull_requests = data.get("pull_requests", {})
        results = []

        for pr_id, pr_data in pull_requests.items():
            if str(pr_data.get("repository_id")) != str(repository_id):
                continue
            if pr_data.get("status") != status:
                continue
            if source_branch_name:
                branch_name = pr_data.get("source_branch_name", "").lower()
                search_branch = source_branch_name.lower()
                if search_branch not in branch_name:
                    continue
            if linked_ticket_id and str(pr_data.get("linked_ticket_id")) != str(
                linked_ticket_id
            ):
                continue
            if pull_request_id and pr_id != pull_request_id:
                continue

            results.append({**pr_data, "pull_request_id": pr_id})

        results.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

        return json.dumps(
            {
                "success": True,
                "count": len(results),
                "pull_requests": results,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, object]:
        return {
            "type": "function",
            "function": {
                "name": "list_pull_requests",
                "description": "List pull requests to view progress and assess PR state. Use this to identify PRs where the branch name matches fix/ticket-ID, check if a PR exists for a development branch, assess PR state, and monitor PR status updates. Optionally filter by source_branch_name to find PRs matching a specific branch pattern (supports partial matching). Returns PRs sorted by most recently updated first.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "Repository ID to view PRs for a specific repository",
                        },
                        "status": {
                            "type": "string",
                            "description": "PR status to filter by",
                            "enum": ["open", "closed", "merged", "draft"],
                        },
                        "source_branch_name": {
                            "type": "string",
                            "description": "Filter by source branch name (supports partial matching, e.g., 'fix/ticket' will match 'fix/ticket-123')",
                        },
                        "linked_ticket_id": {
                            "type": "string",
                            "description": "Filter by linked ticket ID to find PRs associated with a specific ticket",
                        },
                        "pull_request_id": {
                            "type": "string",
                            "description": "Filter by exact pull_request_id",
                        },
                    },
                    "required": ["repository_id", "status"],
                },
            },
        }
