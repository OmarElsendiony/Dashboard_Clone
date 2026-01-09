import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class DeleteBranch(Tool):
    """Tool for deleting a branch from a repository in the version control system."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        branch_id: str,
    ) -> str:
        """
        Delete a branch from a repository.

        Args:
            data: The data dictionary containing all version control system data.
            branch_id: The ID of the branch to delete (required).

        Returns:
            str: A JSON-encoded string containing the success status and deleted branch data.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        branches = data.get("branches", {})
        repositories = data.get("repositories", {})

        # Validate branch_id
        if not branch_id:
            return json.dumps({"success": False, "error": "Missing required parameter: branch_id"})

        if not isinstance(branch_id, str):
            return json.dumps({"success": False, "error": "branch_id must be a string"})

        branch_id = str(branch_id).strip()

        if not branch_id:
            return json.dumps({"success": False, "error": "branch_id cannot be empty"})

        # Find the branch
        if branch_id not in branches:
            return json.dumps({
                "success": False,
                "error": f"Branch with ID '{branch_id}' not found"
            })

        branch = branches[branch_id]

        # Check if it's the default branch
        if branch.get("is_default", False):
            return json.dumps({
                "success": False,
                "error": f"Cannot delete branch '{branch.get('branch_name')}' because it is the default branch"
            })

        # Get repository information for the success message
        repo_id = branch.get("repository_id")
        repo_name = None
        if repo_id and repo_id in repositories:
            repo_name = repositories[repo_id].get("repository_name")

        # Check if repository is archived
        if repo_id and repo_id in repositories:
            repo = repositories[repo_id]
            if repo.get("is_archived", False):
                return json.dumps({
                    "success": False,
                    "error": f"Cannot delete branch in archived repository '{repo.get('repository_name')}'"
                })

        # Delete the branch
        deleted_branch = branches.pop(branch_id)

        # Build success message
        branch_name = deleted_branch.get("branch_name", branch_id)
        if repo_name:
            message = f"Branch '{branch_name}' deleted successfully from repository '{repo_name}'"
        else:
            message = f"Branch '{branch_name}' deleted successfully"

        return json.dumps({
            "success": True,
            "message": message,
            "deleted_branch": deleted_branch
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return the tool specification for the delete_branch function."""
        return {
            "type": "function",
            "function": {
                "name": "delete_branch",
                "description": "Deletes a branch from a repository in the version control system. The branch must exist and cannot be the default branch. Use this after confirming the repository exists using get_repo, the user has admin or write access using get_repo_permissions, and the branch exists and is not the default branch using get_repo_branch. After deletion, verify the branch is removed by calling get_repo_branch and expecting a 'not found' response.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "branch_id": {
                            "type": "string",
                            "description": "The ID of the branch to delete. Required field. The branch must exist and cannot be the default branch of the repository.",
                        },
                    },
                    "required": ["branch_id"],
                },
            },
        }
