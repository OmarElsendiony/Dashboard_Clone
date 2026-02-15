import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class StartBranch(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        branch_type: str,
        creator_id: str,
        description: str,
        ticket_id: Optional[str] = None,
        base_branch: Optional[str] = None,
        issue_id: Optional[str] = None,
        commit_sha: Optional[str] = None,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({
                "output": {
                    "success": False,
                    "message": "Invalid data store."
                }
            })


        if not repository_id:
            return json.dumps({
                "output": {
                    "success": False,
                    "message": "Missing Argument: 'repository_id' is required."
                }
            })

        if not branch_type:
            return json.dumps({
                "output": {
                    "success": False,
                    "message": "Missing Argument: 'branch_type' is required."
                }
            })

        if not creator_id:
            return json.dumps({
                "output": {
                    "success": False,
                    "message": "Missing Argument: 'creator_id' is required."
                }
            })

        if not description:
            return json.dumps({
                "output": {
                    "success": False,
                    "message": "Missing Argument: 'description' is required."
                }
            })

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})
        users = data.get("users", {})
        tickets = data.get("tickets", {})

        if repository_id not in repositories:
            return json.dumps({
                "output": {
                    "success": False,
                    "message": f"Repository {repository_id} does not exist."
                }
            })

        if creator_id not in users:
            return json.dumps({
                "output": {
                    "success": False,
                    "message": f"Creator {creator_id} does not exist."
                }
            })

        allowed_branch_types = ["feat/", "fix/", "hotfix/", "chore/"]
        if branch_type not in allowed_branch_types:
            return json.dumps({
                "output": {
                    "success": False,
                    "message": f"Invalid branch_type. Allowed values are {allowed_branch_types}."
                }
            })

        if ticket_id and ticket_id not in tickets:
            return json.dumps({
                "output": {
                    "success": False,
                    "message": f"Ticket {ticket_id} does not exist."
                }
            })

        if not isinstance(description, str) or not description.strip():
            return json.dumps({
                "output": {
                    "success": False,
                    "message": "Description must be a non-empty string."
                }
            })

        normalized_description = description.strip().lower().replace(" ", "-")

        if ticket_id:
            branch_name = f"{branch_type}{ticket_id}-{normalized_description}"
        else:
            branch_name = f"{branch_type}{normalized_description}"

        for branch in branches.values():
            if branch.get("repository_id") == repository_id and branch.get("branch_name") == branch_name:
                return json.dumps({
                    "output": {
                        "success": False,
                        "error": "Similar branch Detected",
                        "message": f"No-Op: Branch '{branch_name}' already exists in repository {repository_id}.",
                        "branch": branch,
                        "created": False
                    }
                })

        try:
            new_branch_id = str(max([int(bid) for bid in branches.keys() if str(bid).isdigit()], default=0) + 1)
        except ValueError:
             new_branch_id = str(len(branches) + 1)

        new_branch = {
            "branch_id": new_branch_id,
            "repository_id": repository_id,
            "branch_name": branch_name,
            "branch_type": branch_type,
            "creator_id": creator_id,
            "description": description.strip(),
            "ticket_id": ticket_id,
            "base_branch": base_branch,
            "issue_id": issue_id,
            "commit_sha": commit_sha,
            "created_at": "2026-02-02T23:59:00"
        }

        branches[new_branch_id] = new_branch

        return json.dumps({
                "success": True,
                "message": f"Branch created successfully in repository {repository_id}.",
                "branch": new_branch,
                "created": True
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "start_branch",
                "description": (
                    "Creates a new Git branch based on standard naming conventions to keep the repository organized."
                    "PURPOSE: To set up a clean, traceable workspace for code changes, ensuring branch names automatically include the right ticket IDs and descriptions."
                    "WHEN TO USE: When starting work on a new feature or fix, and you want to avoid duplicates by checking if a similar branch already exists before creating a new one."
                    "RETURNS: The branch record (new or existing), including the standardized name and validation status."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "ID of the repository where the branch will be created."
                        },
                        "branch_type": {
                            "type": "string",
                            "enum": ["feat/", "fix/", "hotfix/", "chore/"],
                            "description": "Type of branch to create (Must include trailing slash, e.g., 'feat/')."
                        },
                        "creator_id": {
                            "type": "string",
                            "description": "User ID of the branch creator."
                        },
                        "description": {
                            "type": "string",
                            "description": "Human-readable description used in branch naming."
                        },
                        "ticket_id": {
                            "type": "string",
                            "description": "Ticket ID linked to the branch (optional)."
                        },
                        "base_branch": {
                            "type": "string",
                            "description": "Base branch name used for branching (optional)."
                        },
                        "issue_id": {
                            "type": "string",
                            "description": "Issue tracking ID linked to the branch (optional)."
                        },
                        "commit_sha": {
                            "type": "string",
                            "description": "Specific commit SHA to branch from (optional)."
                        }
                    },
                    "required": [
                        "repository_id",
                        "branch_type",
                        "creator_id",
                        "description"
                    ]
                }
            }
        }
