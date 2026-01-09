import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class UpdateRepoArchiveStatus(Tool):
    """Tool for updating the archive status of a repository in the version control system."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repo_id: str,
        is_archived: bool,
    ) -> str:
        """
        Update the archive status of a repository.

        Args:
            data: The data dictionary containing all version control system data.
            repo_id: The ID of the repository to update (required).
            is_archived: The new archive status (required). Set to True to archive, False to unarchive.

        Returns:
            str: A JSON-encoded string containing the success status and updated repository data.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        repositories = data.get("repositories", {})

        # Validate repo_id
        if not repo_id:
            return json.dumps({"success": False, "error": "Missing required parameter: repo_id"})

        if not isinstance(repo_id, str):
            return json.dumps({"success": False, "error": "repo_id must be a string"})

        repo_id = str(repo_id).strip()

        if not repo_id:
            return json.dumps({"success": False, "error": "repo_id cannot be empty"})

        # Find the repository
        if repo_id not in repositories:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repo_id}' not found"
            })

        repo = repositories[repo_id]

        # Validate is_archived
        if is_archived is None:
            return json.dumps({"success": False, "error": "Missing required parameter: is_archived"})

        if not isinstance(is_archived, bool):
            return json.dumps({"success": False, "error": "is_archived must be a boolean"})

        # Check if the archive status is already the same
        current_is_archived = repo.get("is_archived", False)
        if current_is_archived == is_archived:
            status_str = "archived" if is_archived else "not archived"
            return json.dumps({
                "success": False,
                "error": f"Repository '{repo_id}' is already {status_str}"
            })

        # Update the archive status
        timestamp = "2026-01-01T23:59:00"
        repo["is_archived"] = is_archived
        repo["updated_at"] = timestamp

        action_str = "archived" if is_archived else "unarchived"
        return json.dumps({
            "success": True,
            "message": f"Repository '{repo_id}' has been {action_str} successfully",
            "repo_data": repo
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return the tool specification for the update_repo_archive_status function."""
        return {
            "type": "function",
            "function": {
                "name": "update_repo_archive_status",
                "description": "Updates the archive status of a repository. Use this to archive or unarchive a repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_id": {
                            "type": "string",
                            "description": "The ID of the repository to update.",
                        },
                        "is_archived": {
                            "type": "boolean",
                            "description": "The new archive status. Set to true to archive the repository, false to unarchive it.",
                        },
                    },
                    "required": ["repo_id", "is_archived"],
                },
            },
        }
