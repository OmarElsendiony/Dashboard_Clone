import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpsertRelease(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        access_token: str,
        repository_id: str,
        tag_name: str,
        author_id: str,
        target_type: str,
        target_reference: str,
        release_id: Optional[str] = None,
        release_name: Optional[str] = None,
        description: Optional[str] = None,
        is_draft: bool = False,
        is_prerelease: bool = False
    ) -> str:
        """
        Creates a new release or updates an existing one.
        """
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        timestamp = "2026-01-01T23:59:00"

        try:
            encoded_input_token = base64.b64encode(access_token.encode('utf-8')).decode('utf-8')
        except Exception:
            return json.dumps({"error": "Failed to process access token"})

        tokens = data.get("access_tokens", {})
        valid_token = False
        for token in tokens.values():
            if token.get("token_encoded") == encoded_input_token and token.get("status") == "active":
                if token.get("expires_at") > timestamp:
                    valid_token = True
                    break
        
        if not valid_token:
            return json.dumps({"error": "Invalid or expired access token"})

        releases = data.get("releases", {})
        repositories = data.get("repositories", {})
        users = data.get("users", {})

        if repository_id not in repositories:
            return json.dumps({"error": f"Repository {repository_id} not found"})
        
        if author_id not in users:
            return json.dumps({"error": f"User {author_id} not found"})

        # orrection: Strict validation for target_type enum
        valid_targets = ['commit', 'branch']
        if target_type not in valid_targets:
            return json.dumps({"error": f"Invalid target_type. Must be one of: {', '.join(valid_targets)}"})

        if release_id:
            # Update existing
            if release_id not in releases:
                return json.dumps({"error": f"Release {release_id} not found"})
            
            release = releases[release_id]
            # Update fields
            release["tag_name"] = tag_name
            release["author_id"] = author_id
            release["target_type"] = target_type
            release["target_reference"] = target_reference
            release["is_draft"] = is_draft
            release["is_prerelease"] = is_prerelease
            
            if release_name is not None:
                release["release_name"] = release_name
            if description is not None:
                release["description"] = description
            
            if not is_draft:
                if not release.get("published_at"):
                    release["published_at"] = timestamp
            else:
                release["published_at"] = None
            
            releases[release_id] = release
            return json.dumps(release)

        else:
            # Create new
            new_id = generate_id(releases)
            new_release = {
                "release_id": new_id,
                "repository_id": repository_id,
                "tag_name": tag_name,
                "release_name": release_name,
                "description": description,
                "author_id": author_id,
                "target_type": target_type,
                "target_reference": target_reference,
                "is_draft": is_draft,
                "is_prerelease": is_prerelease,
                "published_at": timestamp if not is_draft else None,
                "created_at": timestamp
            }
            releases[new_id] = new_release
            return json.dumps(new_release)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "upsert_release",
                "description": "Creates a new release or updates an existing one.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "access_token": {
                            "type": "string",
                            "description": "The access token for authentication."
                        },
                        "release_id": {
                            "type": "string",
                            "description": "The ID of the release. If provided, updates the existing release."
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "The ID of the repository."
                        },
                        "tag_name": {
                            "type": "string",
                            "description": "The name of the tag."
                        },
                        "author_id": {
                            "type": "string",
                            "description": "The user ID of the author."
                        },
                        "target_type": {
                            "type": "string",
                            "description": "The type of the target. Allowed values: 'commit', 'branch'."
                        },
                        "target_reference": {
                            "type": "string",
                            "description": "The reference to the target (e.g., commit SHA or branch name)."
                        },
                        "release_name": {
                            "type": "string",
                            "description": "The name of the release."
                        },
                        "description": {
                            "type": "string",
                            "description": "The description of the release."
                        },
                        "is_draft": {
                            "type": "boolean",
                            "description": "Whether the release is a draft (True/False)."
                        },
                        "is_prerelease": {
                            "type": "boolean",
                            "description": "Whether the release is a prerelease (True/False)."
                        }
                    },
                    "required": ["access_token", "repository_id", "tag_name", "author_id", "target_type", "target_reference"]
                }
            }
        }