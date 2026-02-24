import json
import hashlib
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateBranches(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        branch_type: str,
        linked_ticket_id: str,
        created_by: str,
        source_branch_name: Optional[str] = "main",
        issue_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not all([repository_id, branch_type, linked_ticket_id, created_by]):
            return json.dumps({
                "success": False,
                "error": "Missing required arguments: repository_id, branch_type, linked_ticket_id, and created_by are all required."
            })

        repository_id = str(repository_id).strip()
        branch_type = str(branch_type).strip().lower()
        linked_ticket_id = str(linked_ticket_id).strip()
        created_by = str(created_by).strip()
        source_branch_name = str(source_branch_name).strip() if source_branch_name else "main"
        issue_id = str(issue_id).strip() if issue_id else None

        valid_branch_types = ["fix", "feat"]
        if branch_type not in valid_branch_types:
            return json.dumps({
                "success": False,
                "error": f"Policy Violation: branch_type must be strictly one of {valid_branch_types}."
            })

        repositories = data.get("repositories", {})
        users = data.get("users", {})
        branches = data.get("branches", {})
        tickets = data.get("tickets", {})

        if not isinstance(repositories, dict) or not isinstance(users, dict) or not isinstance(branches, dict):
            return json.dumps({"success": False, "error": "Internal data structure error: missing required tables."})

        ticket = tickets.get(linked_ticket_id)
        if not ticket:
            return json.dumps({"success": False, "error": f"Not Found Error: ticket_id '{linked_ticket_id}' not found."})

        ticket_number = ticket.get("ticket_number")
        if not ticket_number:
            return json.dumps({"success": False, "error": f"Data Error: ticket '{linked_ticket_id}' has no ticket_number."})

        repo_exists = False
        for v in repositories.values():
            if isinstance(v, dict) and str(v.get("repository_id")) == repository_id:
                repo_exists = True
                break

        if not repo_exists:
            return json.dumps({"success": False, "error": f"Not Found Error: repository_id '{repository_id}' not found."})

        user_exists = False
        for v in users.values():
            if isinstance(v, dict) and str(v.get("user_id")) == created_by:
                user_exists = True
                break

        if not user_exists:
            return json.dumps({"success": False, "error": f"Not Found Error: user_id (created_by) '{created_by}' not found."})

        branch_name = f"{branch_type}/{ticket_number}"

        for branch in branches.values():
            if isinstance(branch, dict):
                if (str(branch.get("repository_id")) == repository_id and
                    str(branch.get("branch_name")).lower() == branch_name.lower()):
                    return json.dumps({
                        "success": False,
                        "error": "Duplicate Branch Detected",
                        "message": f"A branch named '{branch_name}' already exists in repository '{repository_id}'."
                    })

        max_id = 0
        for k in branches.keys():
            try:
                num = int(str(k))
                if num > max_id:
                    max_id = num
            except ValueError:
                continue

        new_branch_id = str(max_id + 1)
        timestamp = "2026-02-02 23:59:00"

        sha_input = f"{branch_name}-{timestamp}".encode('utf-8')
        mock_commit_sha = hashlib.sha1(sha_input).hexdigest()

        new_branch = {
            "branch_id": new_branch_id,
            "repository_id": repository_id,
            "branch_name": branch_name,
            "source_branch_name": source_branch_name,
            "commit_sha": mock_commit_sha,
            "branch_type": branch_type,
            "linked_ticket_id": linked_ticket_id,
            "issue_id": issue_id,
            "created_by": created_by,
            "status": "active",
            "created_at": timestamp,
            "updated_at": timestamp
        }

        branches[new_branch_id] = new_branch

        return json.dumps({
            "success": True,
            "branch": new_branch,
            "message": f"Branch '{branch_name}' successfully created in repository '{repository_id}'."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_branches",
                "description": (
                    "Creates a new version control branch within a specified repository.\n"
                    " Purpose: Designed to strictly enforce the 'Standardize Code Branches' SOP. It automatically formats the branch name as '[Type]/[Ticket_number]' and restricts the allowed branch types.\n"
                    " When to use: Use this tool when you need to start development work to resolve a bug or build a feature. It should be invoked after discovering the correct repository_id and before committing code or opening a pull request.\n"
                    " Returns: Returns a JSON string containing the newly created branch record (including an auto-generated branch_name, branch_id, and mock commit_sha). Fails if the branch already exists or if an invalid branch_type is provided."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the target repository."
                        },
                        "branch_type": {
                            "type": "string",
                            "enum": ["fix", "feat"],
                            "description": "The category of the branch. Must be 'fix' (for bugs) or 'feat' (for features)."
                        },
                        "linked_ticket_id": {
                            "type": "string",
                            "description": "The identifier of the support ticket this branch addresses. Used to automatically generate the branch_name."
                        },
                        "created_by": {
                            "type": "string",
                            "description": "The unique user identifier of the developer or agent creating the branch."
                        },
                        "source_branch_name": {
                            "type": "string",
                            "description": "The name of the branch to branch off from. Defaults to 'main' if not provided."
                        },
                        "issue_id": {
                            "type": "string",
                            "description": "The optional identifier of the linked engineering issue."
                        }
                    },
                    "required": ["repository_id", "branch_type", "linked_ticket_id", "created_by"]
                }
            }
        }
