import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetCommit(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        commit_sha: str,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        commits = data.get("commits", {})

        # Validate required fields
        if not commit_sha:
            return json.dumps({"success": False, "error": "commit_sha must be provided"})

        if not isinstance(commit_sha, str) or not commit_sha.strip():
            return json.dumps({"success": False, "error": "commit_sha must be a non-empty string"})

        # Normalize input
        commit_sha = commit_sha.strip()

        # Search for commit by commit_sha
        found_commit = None
        for _, commit in commits.items():
            if commit.get("commit_sha") == commit_sha:
                found_commit = commit.copy()
                break

        if not found_commit:
            return json.dumps({
                "success": False,
                "error": f"Commit with SHA '{commit_sha}' not found"
            })

        # Build the response with all relevant commit information
        commit_data = {
            "commit_id": found_commit.get("commit_id"),
            "repository_id": found_commit.get("repository_id"),
            "commit_sha": found_commit.get("commit_sha"),
            "author_id": found_commit.get("author_id"),
            "committer_id": found_commit.get("committer_id"),
            "message": found_commit.get("message"),
            "parent_commit_id": found_commit.get("parent_commit_id"),
            "committed_at": found_commit.get("committed_at"),
            "created_at": found_commit.get("created_at"),
        }

        return json.dumps({
            "success": True,
            "commit_data": commit_data
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_commit",
                "description": "Retrieves detailed information about a commit.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "commit_sha": {
                            "type": "string",
                            "description": "The commit SHA (unique identifier) of the commit to look up.",
                        },
                    },
                    "required": ["commit_sha"],
                },
            },
        }
