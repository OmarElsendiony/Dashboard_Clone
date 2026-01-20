import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateRelease(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repo_id: str,
        tag_name: str,
        release_name: str,
        target_type: str,
        target_reference: str,
        actor_id: str,
        description: Optional[str] = None,
        is_draft: bool = False,
        is_prerelease: bool = False,
    ) -> str:

        def generate_id(table: Dict[str, Any]) -> str:

            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        repositories = data.get("repositories", {})
        users = data.get("users", {})
        releases = data.get("releases", {})
        commits = data.get("commits", {})
        branches = data.get("branches", {})

        # Validate required fields
        if not repo_id:
            return json.dumps({"success": False, "error": "Missing required parameter: repo_id"})

        if not tag_name:
            return json.dumps({"success": False, "error": "Missing required parameter: tag_name"})

        if not isinstance(tag_name, str) or not tag_name.strip():
            return json.dumps({"success": False, "error": "tag_name must be a non-empty string"})

        if not release_name:
            return json.dumps({"success": False, "error": "Missing required parameter: release_name"})

        if not isinstance(release_name, str) or not release_name.strip():
            return json.dumps({"success": False, "error": "release_name must be a non-empty string"})

        if not target_type:
            return json.dumps({"success": False, "error": "Missing required parameter: target_type"})

        if not target_reference:
            return json.dumps({"success": False, "error": "Missing required parameter: target_reference"})

        if not isinstance(target_reference, str) or not target_reference.strip():
            return json.dumps({"success": False, "error": "target_reference must be a non-empty string"})

        if not actor_id:
            return json.dumps({"success": False, "error": "Missing required parameter: actor_id"})

        # Normalize inputs
        repo_id = str(repo_id).strip()
        tag_name = tag_name.strip()
        release_name = release_name.strip()
        target_type = target_type.strip().lower() if isinstance(target_type, str) else ""
        target_reference = target_reference.strip()
        actor_id = str(actor_id).strip()

        # Validate target_type
        allowed_target_types = {"commit", "branch"}
        if target_type not in allowed_target_types:
            return json.dumps({
                "success": False,
                "error": f"target_type must be one of: {', '.join(sorted(allowed_target_types))}"
            })

        # Validate repository exists
        repo = None
        for _, r in repositories.items():
            if str(r.get("repository_id")) == repo_id:
                repo = r
                break

        if not repo:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repo_id}' not found"
            })

        # Check if repository is archived
        if repo.get("is_archived"):
            return json.dumps({
                "success": False,
                "error": f"Cannot create release in archived repository '{repo.get('repository_name')}'"
            })

        # Validate actor exists
        if actor_id not in users:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{actor_id}' not found"
            })

        actor = users[actor_id]

        # Check if actor is active
        if actor.get("status") != "active":
            return json.dumps({
                "success": False,
                "error": f"User '{actor_id}' is not active"
            })

        # Validate target exists based on target_type
        if target_type == "commit":
            # Search for commit by commit_sha
            commit_found = False
            commit_id = None
            for _, commit in commits.items():
                if (
                    str(commit.get("repository_id")) == repo_id
                    and commit.get("commit_sha") == target_reference
                ):
                    commit_found = True
                    commit_id = commit.get("commit_id")
                    break

            if not commit_found:
                return json.dumps({
                    "success": False,
                    "error": f"Commit with SHA '{target_reference}' not found in repository '{repo.get('repository_name')}'"
                })
        elif target_type == "branch":
            # Search for branch by branch_name
            branch_found = False
            branch_id = None
            for _, branch in branches.items():
                if (
                    str(branch.get("repository_id")) == repo_id
                    and branch.get("branch_name") == target_reference
                ):
                    branch_found = True
                    branch_id = branch.get("branch_id")
                    break

            if not branch_found:
                return json.dumps({
                    "success": False,
                    "error": f"Branch '{target_reference}' not found in repository '{repo.get('repository_name')}'"
                })

        # Check if release with tag_name already exists (case-insensitive)
        for _, release in releases.items():
            if (
                str(release.get("repository_id")) == repo_id
                and release.get("tag_name", "").strip().lower() == tag_name.lower()
            ):
                return json.dumps({
                    "success": False,
                    "error": f"Release with tag '{tag_name}' already exists in repository '{repo.get('repository_name')}'"
                })

        # Set timestamp for created_at and published_at
        timestamp = "2026-01-01T23:59:00"

        # Generate new release ID
        new_release_id = generate_id(releases)

        # Process description
        description_value = description.strip() if isinstance(
            description, str) and description.strip() else ""

        # Create new release record
        new_release = {
            "release_id": new_release_id,
            "repository_id": repo_id,
            "tag_name": tag_name,
            "release_name": release_name,
            "description": description_value,
            "author_id": actor_id,
            "target_type": target_type,
            "target_reference": target_reference,
            "is_draft": bool(is_draft),
            "is_prerelease": bool(is_prerelease),
            "published_at": timestamp if not bool(is_draft) else None,
            "created_at": timestamp,
        }

        # Add the new release to the releases dictionary
        releases[new_release_id] = new_release

        return json.dumps({
            "success": True,
            "message": f"Release '{tag_name}' created successfully in repository '{repo.get('repository_name')}'",
            "release_data": new_release
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:

        return {
            "type": "function",
            "function": {
                "name": "create_release",
                "description": "Create a new release in a repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_id": {
                            "type": "string",
                            "description": "The ID of the repository",
                        },
                        "tag_name": {
                            "type": "string",
                            "description": "The tag name for the release",
                        },
                        "release_name": {
                            "type": "string",
                            "description": "The name of the release",
                        },
                        "target_type": {
                            "type": "string",
                            "description": "The type of target: 'commit' or 'branch'",
                            "enum": ["commit", "branch"]
                        },
                        "target_reference": {
                            "type": "string",
                            "description": "The commit SHA or branch name",
                        },
                        "actor_id": {
                            "type": "string",
                            "description": "The ID of the user creating the release",
                        },
                        "description": {
                            "type": "string",
                            "description": "The description of the release (optional)",
                        },
                        "is_draft": {
                            "type": "boolean",
                            "description": "Whether the release is a draft (optional, default: false)",
                        },
                        "is_prerelease": {
                            "type": "boolean",
                            "description": "Whether the release is a prerelease (optional, default: false)",
                        },
                    },
                    "required": ["repo_id", "tag_name", "release_name", "target_type", "target_reference", "actor_id"],
                },
            },
        }
