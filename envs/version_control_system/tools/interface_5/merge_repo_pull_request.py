import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class MergeRepoPullRequest(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        pull_request_id: str,
        actor_id: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        pull_requests = data.get("pull_requests", {})
        users = data.get("users", {})
        repositories = data.get("repositories", {})

        # Validate pull_request_id
        if not pull_request_id:
            return json.dumps({"success": False, "error": "Missing required parameter: pull_request_id"})

        if not isinstance(pull_request_id, str):
            pull_request_id = str(pull_request_id)

        pull_request_id = pull_request_id.strip()

        if not pull_request_id:
            return json.dumps({"success": False, "error": "pull_request_id cannot be empty"})

        # Validate actor_id
        if not actor_id:
            return json.dumps({"success": False, "error": "Missing required parameter: actor_id"})

        if not isinstance(actor_id, str):
            actor_id = str(actor_id)

        actor_id = actor_id.strip()

        if not actor_id:
            return json.dumps({"success": False, "error": "actor_id cannot be empty"})

        # Find the pull request
        found_pr = None
        for _, pr in pull_requests.items():
            if str(pr.get("pull_request_id")) == pull_request_id:
                found_pr = pr
                break

        if not found_pr:
            return json.dumps({
                "success": False,
                "error": f"Pull request with ID '{pull_request_id}' not found"
            })

        # Find the author user
        author = None
        for _, u in users.items():
            if str(u.get("user_id")) == actor_id:
                author = u
                break

        if not author:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{actor_id}' not found"
            })

        # Check if author is active
        if author.get("status") != "active":
            return json.dumps({
                "success": False,
                "error": f"User '{actor_id}' is not active"
            })

        # Check if pull request is already closed or merged
        current_status = found_pr.get("status", "").lower()
        if current_status == "merged":
            return json.dumps({
                "success": False,
                "error": f"Pull request '{pull_request_id}' is already merged"
            })

        if current_status == "closed":
            return json.dumps({
                "success": False,
                "error": f"Pull request '{pull_request_id}' is closed and cannot be merged"
            })

        # Check if the pull request status allows merging (should be 'open')
        if current_status not in {"open", "draft"}:
            return json.dumps({
                "success": False,
                "error": f"Pull request '{pull_request_id}' has status '{current_status}' and cannot be merged"
            })

        # Find the repository to include in the response
        repo_id = str(found_pr.get("repository_id"))
        repo = None
        for _, r in repositories.items():
            if str(r.get("repository_id")) == repo_id:
                repo = r
                break

        # Check if repository is archived
        if repo and repo.get("is_archived"):
            return json.dumps({
                "success": False,
                "error": f"Cannot merge pull request in archived repository '{repo.get('repository_name')}'"
            })

        # Set timestamp for merged_at, closed_at, and updated_at
        timestamp = "2026-01-01T23:59:00"

        # Update the pull request to merged status
        found_pr["status"] = "merged"
        found_pr["merged_by"] = actor_id
        found_pr["merged_at"] = timestamp
        found_pr["closed_at"] = timestamp
        found_pr["updated_at"] = timestamp

        repo_name = repo.get("repository_name") if repo else "unknown"
        pr_number = found_pr.get("pull_request_number")
        pr_author_id = found_pr.get("author_id")

        return json.dumps({
            "success": True,
            "message": f"Pull request #{pr_number} merged successfully in repository '{repo_name}'",
            "pull_request_data": {
                "pull_request_id": found_pr.get("pull_request_id"),
                "repository_id": found_pr.get("repository_id"),
                "pull_request_number": found_pr.get("pull_request_number"),
                "title": found_pr.get("title"),
                "description": found_pr.get("description"),
                "author_id": found_pr.get("author_id"),
                "source_branch": found_pr.get("source_branch"),
                "target_branch": found_pr.get("target_branch"),
                "status": found_pr.get("status"),
                "merged_by": found_pr.get("merged_by"),
                "merged_at": found_pr.get("merged_at"),
                "closed_at": found_pr.get("closed_at"),
                "created_at": found_pr.get("created_at"),
                "updated_at": found_pr.get("updated_at"),
            },
            "pr_author_id": pr_author_id
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "merge_repo_pull_request",
                "description": "Merges a pull request in a repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pull_request_id": {
                            "type": "string",
                            "description": "The ID of the pull request to merge.",
                        },
                        "actor_id": {
                            "type": "string",
                            "description": "The ID of the user performing the merge.",
                        },
                    },
                    "required": ["pull_request_id", "actor_id"],
                },
            },
        }
