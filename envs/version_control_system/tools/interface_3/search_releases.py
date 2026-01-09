import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class SearchReleases(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        author_id: Optional[str] = None,
        tag_name: Optional[str] = None,
        is_draft: Optional[bool] = None,
        is_prerelease: Optional[bool] = None
    ) -> str:
        """
        Searches for releases in a repository with optional filters.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not repository_id:
            return json.dumps({"success": False, "error": "repository_id is required to search releases"})

        repositories = data.get("repositories", {})
        releases = data.get("releases", {})

        # Validate repository exists
        if str(repository_id) not in repositories:
            return json.dumps({"success": False, "error": f"Repository with id '{repository_id}' not found"})

        # Search for releases matching the filters
        results = []
        for release_id, release in releases.items():
            # Filter by repository_id
            if str(release.get("repository_id")) != str(repository_id):
                continue

            # Filter by author_id if provided
            if author_id is not None and str(release.get("author_id")) != str(author_id):
                continue

            # Filter by tag_name if provided
            if tag_name is not None and str(release.get("tag_name")) != str(tag_name):
                continue

            # Filter by is_draft if provided
            if is_draft is not None and release.get("is_draft") != is_draft:
                continue

            # Filter by is_prerelease if provided
            if is_prerelease is not None and release.get("is_prerelease") != is_prerelease:
                continue

            results.append(release)

        return json.dumps({"success": True, "result": results})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "search_releases",
                "description": "Searches for releases in a repository with optional filters. Returns a list of releases matching the criteria.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository to search in."
                        },
                        "author_id": {
                            "type": "string",
                            "description": "Filter by the unique identifier of the release author. Optional."
                        },
                        "tag_name": {
                            "type": "string",
                            "description": "Filter by the release tag name. Optional."
                        },
                        "is_draft": {
                            "type": "boolean",
                            "description": "Filter by draft status. Set to true to find draft releases, false to find published releases. Optional."
                        },
                        "is_prerelease": {
                            "type": "boolean",
                            "description": "Filter by prerelease status. Set to true to find prereleases, false to find stable releases. Optional."
                        }
                    },
                    "required": ["repository_id"]
                }
            }
        }
