import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetPullRequests(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: Optional[str] = None,
        status: Optional[str] = None,
        linked_ticket_id: Optional[str] = None,
        source_branch_name: Optional[str] = None,
        pull_request_id: Optional[str] = None,
        pull_request_number: Optional[int] = None,
        target_branch_name: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not any([repository_id, status, linked_ticket_id, source_branch_name, pull_request_id, pull_request_number, target_branch_name]):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one parameter must be provided",
                }
            )

        if status is not None:
            valid_statuses = ["draft", "open", "closed", "merged"]
            if status not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status '{status}'. Valid values: draft, open, closed, merged",
                    }
                )

        pull_requests = data.get("pull_requests", {})

        results = []
        for pr in pull_requests.values():
            if repository_id is not None and str(pr.get("repository_id")) != str(
                repository_id
            ):
                continue

            if status is not None and pr.get("status") != status:
                continue

            if linked_ticket_id is not None and str(
                pr.get("linked_ticket_id")
            ) != str(linked_ticket_id):
                continue

            if source_branch_name is not None and pr.get(
                "source_branch_name"
            ) != source_branch_name:
                continue

            if pull_request_id is not None and str(pr.get("pull_request_id")) != str(
                pull_request_id
            ):
                continue

            if pull_request_number is not None and pr.get("pull_request_number") != pull_request_number:
                continue

            if target_branch_name is not None and pr.get(
                "target_branch_name"
            ) != target_branch_name:
                continue

            filtered_pr = {
                "pull_request_id": pr.get("pull_request_id"),
                "repository_id": pr.get("repository_id"),
                "pull_request_number": pr.get("pull_request_number"),
                "title": pr.get("title"),
                "source_branch_name": pr.get("source_branch_name"),
                "author_id": pr.get("author_id"),
                "target_branch_name": pr.get("target_branch_name"),
                "status": pr.get("status"),
                "linked_ticket_id": pr.get("linked_ticket_id"),
                "created_at": pr.get("created_at"),
                "updated_at": pr.get("updated_at"),
                "assigned_team_lead": pr.get("assigned_team_lead"),
                "merged_by": pr.get("merged_by"),
                "merged_at": pr.get("merged_at"),
                "closed_at": pr.get("closed_at"),
            }

            results.append(filtered_pr)

        return json.dumps({"success": True, "pull_requests": results})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_pull_requests",
                "description": "Find pull requests by repository, status, linked ticket, branch, or identifier.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "Filter by repository identifier",
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by pull request status",
                            "enum": ["draft", "open", "closed", "merged"],
                        },
                        "linked_ticket_id": {
                            "type": "string",
                            "description": "Filter by linked ticket identifier",
                        },
                        "source_branch_name": {
                            "type": "string",
                            "description": "Filter by source branch name",
                        },
                        "pull_request_id": {
                            "type": "string",
                            "description": "Filter by pull request identifier",
                        },
                        "pull_request_number": {
                            "type": "integer",
                            "description": "Filter by pull request number",
                        },
                        "target_branch_name": {
                            "type": "string",
                            "description": "Filter by target branch name",
                        },
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["repository_id"]},
                        {"required": ["status"]},
                        {"required": ["linked_ticket_id"]},
                        {"required": ["source_branch_name"]},
                        {"required": ["pull_request_id"]},
                        {"required": ["pull_request_number"]},
                        {"required": ["target_branch_name"]},
                     ],
                },
            },
        }
