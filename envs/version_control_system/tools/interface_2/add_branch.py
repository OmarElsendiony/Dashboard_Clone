import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class AddBranch(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        branch_name: str,
        source_branch_name: str,
    ) -> str:
        """Create a new branch in a repository from a source branch."""
        timestamp = "2026-01-01T23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            """Generate a new unique ID for a record."""
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        def find_branch(branches_dict: Dict[str, Any], repository_id_str: str, branch_name_str: str):
            """Find a branch by repository_id and branch_name."""
            for bid, branch in branches_dict.items():
                
                if str(branch.get("repository_id")) == repository_id_str and str(branch.get("branch_name", "")).strip() == branch_name_str:
                    branch_info = branch.copy()
                    branch_info["branch_id"] = str(bid)
                    return branch_info
            
            return None

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        # Get data containers
        branches_dict = data.get("branches", {})
        repositories_dict = data.get("repositories", {})

        repository_id_str = str(repository_id).strip()
        branch_name_str = str(branch_name).strip()
        source_branch_name_str = str(source_branch_name).strip()

        if repository_id_str not in repositories_dict:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repository_id_str}' not found",
            })

        # Find source branch
        source_branch = find_branch(branches_dict, repository_id_str, source_branch_name_str)
        if not source_branch:
            return json.dumps({
                "success": False,
                "error": f"Source branch '{source_branch_name_str}' not found in repository '{repository_id_str}'",
            })

        # Check if branch name already exists in the repository
        existing_branch = find_branch(branches_dict, repository_id_str, branch_name_str)
        if existing_branch:
            return json.dumps({
                "success": False,
                "error": f"Branch '{branch_name_str}' already exists in repository '{repository_id_str}' (branch_id: {existing_branch['branch_id']})",
            })

        # Get commit_sha from source branch
        commit_sha_str = source_branch.get("commit_sha")

        # Create new branch
        new_branch_id = generate_id(branches_dict)
        new_branch = {
            "branch_id": new_branch_id,
            "repository_id": repository_id_str,
            "branch_name": branch_name_str,
            "commit_sha": commit_sha_str,
            "source_branch": source_branch["branch_id"],
            "is_default": False,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        branches_dict[new_branch_id] = new_branch

        return json.dumps({
            "success": True,
            "branch": new_branch,
            "message": f"Branch '{branch_name_str}' created successfully from source branch '{source_branch_name_str}' in repository '{repository_id_str}'",
            "source_branch_name": source_branch_name_str,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return tool metadata for the add_branch function."""
        return {
            "type": "function",
            "function": {
                "name": "add_branch",
                "description": (
                    "Create a new branch in a repository from an existing source branch. "
                    "The new branch will inherit the commit_sha from the source branch. "
                    "Validates that the repository exists. "
                    "Validates that the source branch exists in the repository. "
                    "Validates that the new branch name is unique within the repository. "
                    "The source_branch field in the created branch references the branch_id of the source branch. "
                    "The is_default field is always set to False. "
                    "Returns the created branch details including the auto-generated branch_id."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The ID of the repository where the branch will be created.",
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "The name of the new branch. Must be unique within the repository.",
                        },
                        "source_branch_name": {
                            "type": "string",
                            "description": "The name of the source branch from which this branch is created.",
                        },
                    },
                    "required": ["repository_id", "branch_name", "source_branch_name"],
                },
            },
        }