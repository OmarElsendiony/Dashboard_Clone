
import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class ListReleases(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        is_draft: Optional[bool] = None,
        is_prerelease: Optional[bool] = None,
        author_id: Optional[str] = None
    ) -> str:
        """
        Lists releases for a repository with optional filters.
        """
        releases = data.get("releases", {})
        repositories = data.get("repositories", {})

        if repository_id not in repositories:
            return json.dumps({"error": f"Repository {repository_id} not found"})

        results = []
        for release in releases.values():
            if release.get("repository_id") != repository_id:
                continue
            
            match = True
            if is_draft is not None and release.get("is_draft") != is_draft:
                match = False
            if is_prerelease is not None and release.get("is_prerelease") != is_prerelease:
                match = False
            if author_id is not None and release.get("author_id") != author_id:
                match = False
            
            if match:
                results.append(release)

        return json.dumps(results)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_releases",
                "description": "Lists releases associated with a repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The ID of the repository."
                        },
                        "is_draft": {
                            "type": "boolean",
                            "description": "Filter by draft status (True/False)."
                        },
                        "is_prerelease": {
                            "type": "boolean",
                            "description": "Filter by prerelease status (True/False)."
                        },
                        "author_id": {
                            "type": "string",
                            "description": "Filter by author ID."
                        }
                    },
                    "required": ["repository_id"]
                }
            }
        }