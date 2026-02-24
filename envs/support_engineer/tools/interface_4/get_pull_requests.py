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
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return json.dumps({
                    "success": bool(False),
                    "error": str("Wrong data format"),
                })
        if not isinstance(data, dict):
            return json.dumps({
                "success": bool(False),
                "error": str("Wrong data format"),
            })

        if not any([repository_id, status, linked_ticket_id, source_branch_name, pull_request_id, pull_request_number, target_branch_name]):
            return json.dumps({
                "success": bool(False),
                "error": str("At least one parameter must be provided"),
            })

        if status is not None:
            valid_statuses = ["draft", "open", "closed", "merged"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": bool(False),
                    "error": str(f"Invalid status \"{status}\". Valid values: draft, open, closed, merged"),
                })

        pull_requests = data.get("pull_requests", {})

        results = []
        for pr in pull_requests.values():
            if repository_id is not None and str(pr.get("repository_id")) != str(repository_id):
                continue

            if status is not None and str(pr.get("status")) != str(status):
                continue

            if linked_ticket_id is not None and str(pr.get("linked_ticket_id")) != str(linked_ticket_id):
                continue

            if source_branch_name is not None and str(pr.get("source_branch_name")) != str(source_branch_name):
                continue

            if pull_request_id is not None and str(pr.get("pull_request_id")) != str(pull_request_id):
                continue

            if pull_request_number is not None and int(pr.get("pull_request_number")) != int(pull_request_number):
                continue

            if target_branch_name is not None and str(pr.get("target_branch_name")) != str(target_branch_name):
                continue

            pull_request_id_val = pr.get("pull_request_id")
            repository_id_val = pr.get("repository_id")
            pull_request_number_val = pr.get("pull_request_number")
            title_val = pr.get("title")
            source_branch_name_val = pr.get("source_branch_name")
            author_id_val = pr.get("author_id")
            target_branch_name_val = pr.get("target_branch_name")
            status_val = pr.get("status")
            linked_ticket_id_val = pr.get("linked_ticket_id")
            created_at_val = pr.get("created_at")
            updated_at_val = pr.get("updated_at")
            assigned_team_lead_val = pr.get("assigned_team_lead")
            merged_by_val = pr.get("merged_by")
            merged_at_val = pr.get("merged_at")
            closed_at_val = pr.get("closed_at")

            filtered_pr = {
                "pull_request_id": str(pull_request_id_val) if pull_request_id_val is not None else None,
                "repository_id": str(repository_id_val) if repository_id_val is not None else None,
                "pull_request_number": int(pull_request_number_val) if pull_request_number_val is not None else None,
                "title": str(title_val) if title_val is not None else None,
                "source_branch_name": str(source_branch_name_val) if source_branch_name_val is not None else None,
                "author_id": str(author_id_val) if author_id_val is not None else None,
                "target_branch_name": str(target_branch_name_val) if target_branch_name_val is not None else None,
                "status": str(status_val) if status_val is not None else None,
                "linked_ticket_id": str(linked_ticket_id_val) if linked_ticket_id_val is not None else None,
                "created_at": str(created_at_val) if created_at_val is not None else None,
                "updated_at": str(updated_at_val) if updated_at_val is not None else None,
                "assigned_team_lead": str(assigned_team_lead_val) if assigned_team_lead_val is not None else None,
                "merged_by": str(merged_by_val) if merged_by_val is not None else None,
                "merged_at": str(merged_at_val) if merged_at_val is not None else None,
                "closed_at": str(closed_at_val) if closed_at_val is not None else None,
            }

            results.append(filtered_pr)

        return json.dumps({
            "success": bool(True),
            "pull_requests": results,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_pull_requests",
                "description": "Finds pull requests matching specified filter criteria.",
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
