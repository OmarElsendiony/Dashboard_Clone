import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetRelease(Tool):
    """Tool for retrieving release details from the version control system."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repo_id: str,
        tag_name: str,
    ) -> str:
        """
        Retrieve release details by repository ID and tag name.

        Args:
            data: The data dictionary containing all version control system data.
            repo_id: The ID of the repository containing the release (required).
            tag_name: The tag name of the release to look up (required).

        Returns:
            JSON string containing the success status and release data if found.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        releases = data.get("releases", {})
        repositories = data.get("repositories", {})

        # Validate required fields
        if not repo_id or not str(repo_id).strip():
            return json.dumps({"success": False, "error": "repo_id must be provided"})

        if not tag_name:
            return json.dumps({"success": False, "error": "tag_name must be provided"})

        if not isinstance(tag_name, str) or not tag_name.strip():
            return json.dumps({"success": False, "error": "tag_name must be a non-empty string"})

        # Normalize inputs
        repo_id = str(repo_id).strip()
        tag_name = tag_name.strip()

        # Validate repository exists
        repo_found = False
        for _, repo in repositories.items():
            if str(repo.get("repository_id")) == repo_id:
                repo_found = True
                break

        if not repo_found:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repo_id}' not found"
            })

        # Search for release by repository_id and tag_name (case-insensitive)
        found_release = None
        for _, release in releases.items():
            if (
                str(release.get("repository_id")) == repo_id
                and release.get("tag_name", "").strip().lower() == tag_name.lower()
            ):
                found_release = release.copy()
                break

        if not found_release:
            return json.dumps({
                "success": False,
                "error": f"Release with tag '{tag_name}' not found in repository '{repo_id}'"
            })

        # Build the response with release data
        release_data = {
            "release_id": found_release.get("release_id"),
            "repository_id": found_release.get("repository_id"),
            "tag_name": found_release.get("tag_name"),
            "release_name": found_release.get("release_name"),
            "description": found_release.get("description"),
            "author_id": found_release.get("author_id"),
            "target_type": found_release.get("target_type"),
            "target_reference": found_release.get("target_reference"),
            "is_draft": found_release.get("is_draft"),
            "is_prerelease": found_release.get("is_prerelease"),
            "published_at": found_release.get("published_at"),
            "created_at": found_release.get("created_at"),
        }

        return json.dumps({
            "success": True,
            "release_data": release_data
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return the tool specification for the get_release function."""
        return {
            "type": "function",
            "function": {
                "name": "get_release",
                "description": "Retrieves detailed information about a release from a repository by tag name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_id": {
                            "type": "string",
                            "description": "The ID of the repository containing the release.",
                        },
                        "tag_name": {
                            "type": "string",
                            "description": "The tag name of the release to look up.",
                        },
                    },
                    "required": ["repo_id", "tag_name"],
                },
            },
        }
