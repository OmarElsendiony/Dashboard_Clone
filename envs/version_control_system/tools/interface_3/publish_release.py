import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class PublishRelease(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        tag_name: str,
        author_id: str,
        release_name: Optional[str] = None,
        description: Optional[str] = None,
        target_type: Optional[str] = None,
        target_reference: Optional[str] = None,
        is_draft: Optional[bool] = None,
        is_prerelease: Optional[bool] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not repository_id:
            return json.dumps({"success": False, "error": "repository_id is required to publish a release"})
        if not tag_name:
            return json.dumps({"success": False, "error": "tag_name is required to publish a release"})
        if not author_id:
            return json.dumps({"success": False, "error": "author_id is required to publish a release"})

        # Validate target_type if provided
        if target_type is not None:
            valid_target_types = ["commit", "branch"]
            if target_type not in valid_target_types:
                return json.dumps({"success": False, "error": f"Invalid target_type '{target_type}'. Valid values: commit, branch"})

        # Set defaults for boolean fields
        if is_draft is None:
            is_draft = False
        if is_prerelease is None:
            is_prerelease = False

        repositories = data.get("repositories", {})
        users = data.get("users", {})
        releases = data.get("releases", {})

        # Validate repository exists
        if str(repository_id) not in repositories:
            return json.dumps({"success": False, "error": f"Repository with id '{repository_id}' not found"})

        # Validate author exists
        if str(author_id) not in users:
            return json.dumps({"success": False, "error": f"User with id '{author_id}' not found"})

        # Generate new release_id
        if releases:
            max_id = max(int(k) for k in releases.keys())
            new_release_id = str(max_id + 1)
        else:
            new_release_id = "1"

        # Set published_at if not a draft
        published_at = None if is_draft else "2026-01-01T23:59:00"

        # Create release record
        new_release = {
            "release_id": new_release_id,
            "repository_id": repository_id,
            "tag_name": tag_name,
            "release_name": release_name,
            "description": description,
            "author_id": author_id,
            "target_type": target_type,
            "target_reference": target_reference,
            "is_draft": bool(is_draft),
            "is_prerelease": bool(is_prerelease),
            "published_at": published_at,
            "created_at": "2026-01-01T23:59:00"
        }

        releases[new_release_id] = new_release

        return json.dumps({"success": True, "result": new_release})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "publish_release",
                "description": "Publishes a new release in a repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository where the release will be published."
                        },
                        "tag_name": {
                            "type": "string",
                            "description": "The tag name for the release (e.g., v1.0.0)."
                        },
                        "author_id": {
                            "type": "string",
                            "description": "The unique identifier of the user publishing the release."
                        },
                        "release_name": {
                            "type": "string",
                            "description": "The display name for the release (optional)."
                        },
                        "description": {
                            "type": "string",
                            "description": "The release notes or description (optional)."
                        },
                        "target_type": {
                            "type": "string",
                            "description": "The type of target for the release. Valid values: commit, branch (optional)."
                        },
                        "target_reference": {
                            "type": "string",
                            "description": "The commit SHA or branch name that the release points to (optional)."
                        },
                        "is_draft": {
                            "type": "boolean",
                            "description": "Whether the release is a draft. Draft releases are not published. Default: false (optional)."
                        },
                        "is_prerelease": {
                            "type": "boolean",
                            "description": "Whether the release is a prerelease (e.g., alpha, beta, rc). Default: false (optional)."
                        }
                    },
                    "required": ["repository_id", "tag_name", "author_id"]
                }
            }
        }
