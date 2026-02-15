import json
from typing import Dict, Optional, Any
from tau_bench.envs.tool import Tool


class CreateNewBranch(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_name: str,
        branch_name: str,
        user_email: Optional[str] = None,
    ) -> str:
        if not repository_name:
            return json.dumps({"error": "repository_name is required"})

        if not branch_name:
            return json.dumps({"error": "branch_name is required"})

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})
        users = data.get("users", {})
        timestamp = "2026-02-02 23:59:00"

        repository_id = None
        default_branch_name = None
        for r_id, repo in repositories.items():
            if repo.get("repository_name") == str(repository_name):
                repository_id = r_id
                default_branch_name = repo.get("default_branch", "main")
                break

        if not repository_id:
            return json.dumps({"error": f"Repository with name '{repository_name}' not found"})

        main_branch_details = None
        for branch in branches.values():
            if (
                branch.get("branch_name") == str(default_branch_name) and
                str(branch.get("repository_id")) == str(repository_id)
            ):
                main_branch_details = branch
                break

        if not main_branch_details:
            return json.dumps(
                {"error": f"Main branch '{default_branch_name}' not found in repository '{repository_name}'"}
            )

        for branch in branches.values():
            if (
                branch.get("branch_name") == str(branch_name) and
                str(branch.get("repository_id")) == str(repository_id)
            ):
                return json.dumps(
                    {"error": f"Branch '{branch_name}' already exists in repository '{repository_name}'"}
                )

        created_by = None
        if user_email:
            for u_id, user in users.items():
                if user.get("email") == str(user_email):
                    created_by = u_id
                    break

            if not created_by:
                return json.dumps({"error": f"User with email '{user_email}' not found"})

        if not branches:
            branch_id = "1"
        else:
            branch_id = str(max(int(k) for k in branches.keys()) + 1)

        new_branch = {
            "branch_id": str(branch_id),
            "repository_id": str(repository_id),
            "branch_name": str(branch_name),
            "source_branch_name": str(default_branch_name),
            "commit_sha": str(main_branch_details["commit_sha"]) if main_branch_details.get("commit_sha") else None,
            "linked_ticket_id": None,
            "created_by": str(created_by) if created_by else None,
            "status": "active",
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        branches[branch_id] = new_branch

        return json.dumps({
            "success": True,
            "branch": {
                "branch_id": str(new_branch["branch_id"]),
                "repository_id": str(new_branch["repository_id"]),
                "branch_name": str(new_branch["branch_name"]),
                "source_branch_name": str(new_branch["source_branch_name"]),
                "commit_sha": new_branch["commit_sha"],
                "linked_ticket_id": None,
                "created_by": new_branch["created_by"],
                "created_at": str(new_branch["created_at"]),
                "updated_at": str(new_branch["updated_at"]),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_new_branch",
                "description": "Creates a new branch in a repository from the main branch. It should be used when you need to create a new branch for development work.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_name": {
                            "type": "string",
                            "description": "The name of the repository",
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "The name of the new branch",
                        },
                        "user_email": {
                            "type": "string",
                            "description": "The email of the user creating the branch",
                        },
                    },
                    "required": ["repository_name", "branch_name"],
                },
            },
        }
