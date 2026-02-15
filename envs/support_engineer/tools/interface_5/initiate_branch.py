import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool
import hashlib


class InitiateBranch(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        branch_name: str,
        created_by: str,
        source_branch: Optional[str] = None,
        branch_type: str = "hotfix",
        linked_ticket_id: Optional[str] = None,
        issue_id: Optional[str] = None,

    ) -> str:
        def generate_id(table: Dict[str, Any]) -> str:
            return str(max([int(k) for k in table.keys()], default=0) + 1)

        if not repository_id:
            return json.dumps(
                {
                    "success": False,
                    "error": "Repository ID cannot be empty",
                }
            )
        if not branch_name:
            return json.dumps(
                {
                    "success": False,
                    "error": "Branch name cannot be empty",
                }
            )
        if not created_by:
            return json.dumps(
                {
                    "success": False,
                    "error": "Created by user ID cannot be empty",
                }
            )

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )
        base_commit_sha = hashlib.sha1(f"{repository_id}-{branch_name or 'main'}".encode()).hexdigest()
        branches = data.get("branches", {})
        issues = data.get("issues", {})
        tickets = data.get("tickets", {})
        # validate linked_ticket_id if provided
        if linked_ticket_id and linked_ticket_id not in tickets:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Ticket with ID '{linked_ticket_id}' does not exist",
                }
            )
        # validate issue_id if provided
        if issue_id and issue_id not in issues:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Issue with ID '{issue_id}' does not exist",
                }
            )
        # validate branch_name uniqueness within the repository
        for branch in branches.values():
            if branch["repository_id"] == repository_id and branch["branch_name"] == branch_name:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Branch name '{branch_name}' already exists in repository '{repository_id}'",
                    }
                )
        if not repository_id:
            return json.dumps(
                {
                    "success": False,
                    "error": "Repository ID cannot be empty",
                }
            )
        if not branch_name:
            return json.dumps(
                {
                    "success": False,
                    "error": "Branch name cannot be empty",
                }
            )
        if not created_by:
            return json.dumps(
                {
                    "success": False,
                    "error": "Created by user ID cannot be empty",
                }
            )
        users = data.get("users", {})
        if created_by not in users:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with ID '{created_by}' does not exist",
                }
            )
        # validate branch_type
        if branch_type not in ['fix', 'feat', 'chore', 'hotfix']:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid branch type '{branch_type}', must be one of ['fix', 'feat', 'chore', 'hotfix']",
                }
            )
        target_repo = data.get("repositories", {}).get(repository_id)
        if not target_repo:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Repository with ID '{repository_id}' does not exist",
                }
            )
        source_branch_name = source_branch or target_repo.get("default_branch", "main")
        sb = None
        # find source branch
        for branch in branches.values():
            if branch["repository_id"] == repository_id and branch["branch_name"] == source_branch_name:
                sb = branch
                break
        if not sb:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Source branch '{source_branch_name}' does not exist in repository '{repository_id}'",
                }
            )
        # get source branch commit sha
        sb_commit_sha = sb.get("commit_sha", None)
        new_branch = {
            "branch_id": generate_id(branches),
            "repository_id": str(repository_id),
            "branch_name": str(branch_name),
            "source_branch_name": str(source_branch_name),
            "commit_sha": sb_commit_sha if sb_commit_sha else base_commit_sha,
            "branch_type": str(branch_type),
            "linked_ticket_id": str(linked_ticket_id) if linked_ticket_id else None,
            "issue_id": str(issue_id) if issue_id else None,
            "created_by": str(created_by),
            "status": "active",
            "created_at": "2026-02-02 23:59:00",
            "updated_at": "2026-02-02 23:59:00"
        }
        branches[new_branch["branch_id"]] = new_branch
        data["branches"] = branches
        return json.dumps(
            {
                "success": True,
                "branch": new_branch
            }
        )


    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "initiate_branch",
                "description": "Initiate a new development branch within a repository to isolate code changes for a specific ticket or issue.  Use this to initialize the technical environment for addressing a support request or bug report.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The ID of the repository where the branch will be created.",
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "The name of the new branch to be created.",
                        },
                        "source_branch": {
                            "type": "string",
                            "description": "The source branch from which to create the new branch. Defaults to the repository's default branch if not provided.",
                        },
                        "branch_type": {
                            "type": "string",
                            "description": "The type of the branch being created.",
                            "enum": ["fix", "feat", "chore", "hotfix"],
                            "default": "hotfix"
                        },
                        "linked_ticket_id": {
                            "type": "string",
                            "description": "The ID of the ticket that this branch is linked to.",
                        },
                        "issue_id": {
                            "type": "string",
                            "description": "The ID of the issue that this branch is linked to.",
                        },
                        "created_by": {
                            "type": "string",
                            "description": "The ID of the user creating the branch.",
                        },
                    },
                    "required": ["repository_id", "branch_name", "created_by"],
                },
            },
        }
