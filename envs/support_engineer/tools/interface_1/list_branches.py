import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ListBranches(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        status: Optional[str] = None,
        branch_type: Optional[str] = None,
        created_by: Optional[str] = None,
        linked_ticket_id: Optional[str] = None,
        issue_id: Optional[str] = None,
        name_contains: Optional[str] = None,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })

        if not repository_id:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'repository_id' is required."
            })

        if not isinstance(repository_id, str) or not repository_id.strip():
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: repository_id must be a non-empty string."
            })

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})

        if not isinstance(repositories, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'repositories' must be a dictionary"
            })

        if not isinstance(branches, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'branches' must be a dictionary"
            })

        repo_key = str(repository_id)
        if repo_key not in repositories:
            return json.dumps({
                "success": False,
                "error": f"Foreign Key Error: repository_id '{repository_id}' not found."
            })

        valid_statuses = ["active", "merged", "deleted"]
        valid_branch_types = ["fix", "feat", "chore", "hotfix"]

        if status is not None and status not in valid_statuses:
            return json.dumps({
                "success": False,
                "error": f"Invalid Argument: status must be one of {valid_statuses}."
            })

        if branch_type is not None and branch_type not in valid_branch_types:
            return json.dumps({
                "success": False,
                "error": f"Invalid Argument: branch_type must be one of {valid_branch_types}."
            })

        if created_by is not None and (not isinstance(created_by, str) or not created_by.strip()):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: created_by must be a non-empty string when provided."
            })

        if linked_ticket_id is not None and (not isinstance(linked_ticket_id, str) or not linked_ticket_id.strip()):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: linked_ticket_id must be a non-empty string when provided."
            })

        if issue_id is not None and (not isinstance(issue_id, str) or not issue_id.strip()):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: issue_id must be a non-empty string when provided."
            })

        if name_contains is not None and (not isinstance(name_contains, str) or not name_contains.strip()):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: name_contains must be a non-empty string when provided."
            })

        needle = name_contains.lower().strip() if name_contains is not None else None

        result = []

        for b in branches.values():
            if not isinstance(b, dict):
                continue

            if str(b.get("repository_id", "")) != repo_key:
                continue

            if status is not None and b.get("status") != status:
                continue

            if branch_type is not None and b.get("branch_type") != branch_type:
                continue

            if created_by is not None and str(b.get("created_by", "")) != str(created_by):
                continue

            if linked_ticket_id is not None and str(b.get("linked_ticket_id", "")) != str(linked_ticket_id):
                continue

            if issue_id is not None and str(b.get("issue_id", "")) != str(issue_id):
                continue

            if needle is not None:
                bn = str(b.get("branch_name", "")).lower()
                if needle not in bn:
                    continue

            result.append(b)

        result.sort(
            key=lambda x: (
                str(x.get("branch_name", "")).lower(),
                str(x.get("branch_id", "")),
            )
        )

        return json.dumps({
            "success": True,
            "branches": result,
            "count": len(result),
            "message": f"Branches retrieved successfully for repository {repository_id}."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_branches",
                "description": (
                    "Lists source control branches for a repository along with branch metadata and workflow linkage details."
                    "PURPOSE: Provides visibility into active and historical development branches to support engineering coordination and traceability."
                    "WHEN TO USE: When reviewing repository work status, tracking fixes or features, or correlating branches to tickets or issues."
                    "RETURNS: A list of branch records including state, category, and linked workflow references."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "Repository identifier."
                        },
                        "status": {
                            "type": "string",
                            "enum": ["active", "merged", "deleted"],
                            "description": "Filter branches by branch status (optional )"
                        },
                        "branch_type": {
                            "type": "string",
                            "enum": ["fix", "feat", "chore", "hotfix"],
                            "description": "Filter branches by branch type (optional )"
                        },
                        "created_by": {
                            "type": "string",
                            "description": "Filter branches by creator identifier (optional )"
                        },
                        "linked_ticket_id": {
                            "type": "string",
                            "description": "Filter branches by linked support ticket identifier (optional )"
                        },
                        "issue_id": {
                            "type": "string",
                            "description": "Filter branches by linked issue identifier (optional )"
                        },
                        "name_contains": {
                            "type": "string",
                            "description": "Filter branches by substring match on branch name (optional )"
                        }
                    },
                    "required": ["repository_id"]
                }
            }
        }
