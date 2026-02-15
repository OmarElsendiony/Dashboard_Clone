import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateBranch(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        branch_name: str,
        created_by: str,
        source_branch_name: Optional[str] = None,
        branch_type: Optional[str] = None,
        linked_ticket_id: Optional[str] = None,
    ) -> str:
        timestamp = "2026-02-02 23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        def find_branch_by_name(branches_dict: Dict[str, Any], repository_id_str: str, branch_name_str: str) -> tuple:
            for bid, branch in branches_dict.items():
                if not isinstance(branch, dict):
                    continue
                if (str(branch.get("repository_id")) == repository_id_str and
                    str(branch.get("branch_name", "")).strip() == branch_name_str):
                    return str(bid), branch
            return None, None

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        if not repository_id:
            return json.dumps({"success": False, "error": "Missing required parameter: 'repository_id'"})

        if not branch_name:
            return json.dumps({"success": False, "error": "Missing required parameter: 'branch_name'"})

        if not created_by:
            return json.dumps({"success": False, "error": "Missing required parameter: 'created_by'"})

        repositories_dict = data.get("repositories", {})
        branches_dict = data.get("branches", {})
        users_dict = data.get("users", {})
        tickets_dict = data.get("tickets", {})

        repository_id_str = str(repository_id).strip()
        branch_name_str = str(branch_name).strip()
        source_branch_name_str = str(source_branch_name).strip() if source_branch_name else None
        created_by_str = str(created_by).strip()
        branch_type_str = str(branch_type).strip() if branch_type else None
        linked_ticket_id_str = str(linked_ticket_id).strip() if linked_ticket_id else None

        if not branch_name_str:
            return json.dumps({
                "success": False,
                "error": "Branch name cannot be empty"
            })

        if repository_id_str not in repositories_dict:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repository_id_str}' not found"
            })

        repository = repositories_dict[repository_id_str]

        if not isinstance(repository, dict):
            return json.dumps({
                "success": False,
                "error": f"Invalid repository data structure for repository ID '{repository_id_str}'"
            })

        if created_by_str not in users_dict:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{created_by_str}' not found"
            })

        creator = users_dict[created_by_str]

        if not isinstance(creator, dict):
            return json.dumps({
                "success": False,
                "error": f"Invalid user data structure for user ID '{created_by_str}'"
            })

        creator_status = creator.get("status")
        if creator_status != 'active':
            return json.dumps({
                "success": False,
                "error": f"User '{created_by_str}' is not active and cannot create branches"
            })

        source_branch_id_str = None
        source_branch = None
        source_commit_sha = None

        if source_branch_name_str:
            source_branch_id_str, source_branch = find_branch_by_name(branches_dict, repository_id_str, source_branch_name_str)

            if not source_branch_id_str or not source_branch:
                return json.dumps({
                    "success": False,
                    "error": f"Source branch '{source_branch_name_str}' not found in repository '{repository_id_str}'"
                })

            source_branch_status = str(source_branch.get("status", "")).strip()
            if source_branch_status != 'active':
                return json.dumps({
                    "success": False,
                    "error": f"Source branch '{source_branch_name_str}' has status '{source_branch_status}' and cannot be used as a source. Only active branches can be used as source."
                })

            source_commit_sha = source_branch.get("commit_sha")

        existing_branch_id, _ = find_branch_by_name(branches_dict, repository_id_str, branch_name_str)

        if existing_branch_id:
            return json.dumps({
                "success": False,
                "error": f"Branch '{branch_name_str}' already exists in repository '{repository_id_str}' (branch_id: {existing_branch_id})"
            })

        if branch_type_str:
            valid_branch_types = ['fix', 'feat', 'chore', 'hotfix']
            if branch_type_str not in valid_branch_types:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid branch type '{branch_type_str}'. Must be one of: {', '.join(valid_branch_types)}"
                })

        if linked_ticket_id_str:
            if linked_ticket_id_str not in tickets_dict:
                return json.dumps({
                    "success": False,
                    "error": f"Linked ticket with ID '{linked_ticket_id_str}' not found"
                })

            linked_ticket = tickets_dict[linked_ticket_id_str]
            if not isinstance(linked_ticket, dict):
                return json.dumps({
                    "success": False,
                    "error": f"Invalid ticket data structure for ticket ID '{linked_ticket_id_str}'"
                })

            ticket_status = str(linked_ticket.get("status", "")).strip()
            if ticket_status in ['archived']:
                return json.dumps({
                    "success": False,
                    "error": f"Cannot link to ticket '{linked_ticket_id_str}' with status '{ticket_status}'"
                })

        new_branch_id = generate_id(branches_dict)
        new_branch = {
            "branch_id": new_branch_id,
            "repository_id": repository_id_str,
            "branch_name": branch_name_str,
            "source_branch_name": source_branch_name_str,
            "commit_sha": source_commit_sha,
            "branch_type": branch_type_str,
            "linked_ticket_id": linked_ticket_id_str,
            "issue_id": None,
            "created_by": created_by_str,
            "status": "active",
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        branches_dict[new_branch_id] = new_branch

        branch_return = new_branch.copy()
        branch_return["creator_email"] = creator.get("email")
        branch_return["creator_name"] = f"{creator.get('first_name', '')} {creator.get('last_name', '')}".strip()
        branch_return["repository_name"] = repository.get("repository_name")
        branch_return["source_branch_id"] = source_branch_id_str

        if source_branch_name_str:
            message = f"Branch '{branch_name_str}' created successfully in repository '{repository.get('repository_name', repository_id_str)}' from source branch '{source_branch_name_str}'"
        else:
            message = f"Branch '{branch_name_str}' created successfully in repository '{repository.get('repository_name', repository_id_str)}' with no source branch"

        return json.dumps({
            "success": True,
            "branch": branch_return,
            "message": message,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_branch",
                "description": (
                    "Creates a new branch in a repository, optionally from an existing source branch. "
                    "This function establishes an independent line of development for implementing fixes, features, or changes. "
                    "Use this when starting work on ticket fixes, developing new features, creating hotfixes for critical issues, "
                    "isolating experimental changes from the main codebase, or creating a new initial branch in a repository. "
                    "If no source branch is specified, the branch is created with no commit history."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository where the branch will be created.",
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "The name for the new branch. Must be unique within the repository.",
                        },
                        "created_by": {
                            "type": "string",
                            "description": "The unique identifier of the user creating the branch.",
                        },
                        "source_branch_name": {
                            "type": "string",
                            "description": "Optional. The name of the existing branch to use as the starting point. If not provided, branch is created with no commit history.",
                        },
                        "branch_type": {
                            "type": "string",
                            "description": "Optional. The type of branch being created.",
                            "enum" : ["fix", "feat", "chore", "hotfix"],
                        },
                        "linked_ticket_id": {
                            "type": "string",
                            "description": "Optional. The unique identifier of the ticket this branch addresses.",
                        },
                    },
                    "required": ["repository_id", "branch_name", "created_by"],
                },
            },
        }
