import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class UpdateBranchHead(Tool):
    """Tool for updating the HEAD commit SHA of a branch in the version control system."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        branch_id: str,
        commit_sha: str,
    ) -> str:
        """
        Update the HEAD commit SHA of a branch.

        Args:
            data: The data dictionary containing all version control system data.
            branch_id: The ID of the branch to update (required).
            commit_sha: The commit SHA to set as the branch HEAD (required).

        Returns:
            JSON string containing the success status and updated branch data.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        branches = data.get("branches", {})
        commits = data.get("commits", {})

        # Validate required fields
        if not branch_id:
            return json.dumps({"success": False, "error": "Missing required parameter: branch_id"})

        if not commit_sha:
            return json.dumps({"success": False, "error": "Missing required parameter: commit_sha"})

        if not isinstance(branch_id, str) or not branch_id.strip():
            return json.dumps({"success": False, "error": "branch_id must be a non-empty string"})

        if not isinstance(commit_sha, str) or not commit_sha.strip():
            return json.dumps({"success": False, "error": "commit_sha must be a non-empty string"})

        # Normalize input
        branch_id = branch_id.strip()
        commit_sha = commit_sha.strip()

        # Validate branch exists
        branch = None
        for b_id, b in branches.items():
            if str(b.get("branch_id")) == branch_id:
                branch = b
                break

        if not branch:
            return json.dumps({
                "success": False,
                "error": f"Branch with ID '{branch_id}' not found"
            })

        # Validate commit exists by commit_sha
        found_commit = None
        for _, commit in commits.items():
            if commit.get("commit_sha") == commit_sha:
                found_commit = commit
                break

        if not found_commit:
            return json.dumps({
                "success": False,
                "error": f"Commit with SHA '{commit_sha}' not found"
            })

        # Set timestamp for updated_at
        timestamp = "2026-01-01T23:59:00"

        # Update branch HEAD to point to the new commit SHA
        branch["commit_sha"] = commit_sha
        branch["updated_at"] = timestamp

        # Build response with updated branch data
        branch_data = {
            "branch_id": branch.get("branch_id"),
            "repository_id": branch.get("repository_id"),
            "branch_name": branch.get("branch_name"),
            "commit_sha": branch.get("commit_sha"),
            "source_branch": branch.get("source_branch"),
            "is_default": branch.get("is_default"),
            "created_at": branch.get("created_at"),
            "updated_at": branch.get("updated_at"),
        }

        return json.dumps({
            "success": True,
            "message": f"Branch HEAD updated successfully to commit '{commit_sha}'",
            "branch_data": branch_data
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return the tool specification for the update_branch_head function."""
        return {
            "type": "function",
            "function": {
                "name": "update_branch_head",
                "description": "Updates the HEAD commit SHA of a branch in the version control system. This function moves the branch HEAD pointer to point to a specific commit.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "branch_id": {
                            "type": "string",
                            "description": "The ID of the branch to update.",
                        },
                        "commit_sha": {
                            "type": "string",
                            "description": "The commit SHA to set as the branch HEAD.",
                        },
                    },
                    "required": ["branch_id", "commit_sha"],
                },
            },
        }
