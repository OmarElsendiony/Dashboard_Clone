import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class OpenPullRequest(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        title: str,
        source_branch_id: str,
        target_branch_id: str,
        author_id: str,
        description: Optional[str] = None,
        status: Optional[str] = "open"
    ) -> str:
        """
        Opens a new pull request in a repository.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not repository_id:
            return json.dumps({"success": False, "error": "repository_id is required to open pull request"})
        if not title:
            return json.dumps({"success": False, "error": "title is required to open pull request"})
        if not source_branch_id:
            return json.dumps({"success": False, "error": "source_branch_id is required to open pull request"})
        if not target_branch_id:
            return json.dumps({"success": False, "error": "target_branch_id is required to open pull request"})
        if not author_id:
            return json.dumps({"success": False, "error": "author_id is required to open pull request"})

        # Validate status
        valid_statuses = ["open", "draft", "closed", "merged"]
        if status not in valid_statuses:
            return json.dumps({"success": False, "error": f"Invalid status '{status}'. Valid values: open, draft, closed, merged"})

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})
        users = data.get("users", {})
        pull_requests = data.get("pull_requests", {})

        # Validate repository exists
        if str(repository_id) not in repositories:
            return json.dumps({"success": False, "error": f"Repository with id '{repository_id}' not found"})

        # Validate source branch exists
        if str(source_branch_id) not in branches:
            return json.dumps({"success": False, "error": f"Source branch with id '{source_branch_id}' not found"})

        # Validate target branch exists
        if str(target_branch_id) not in branches:
            return json.dumps({"success": False, "error": f"Target branch with id '{target_branch_id}' not found"})

        # Validate source and target branches are different
        if source_branch_id == target_branch_id:
            return json.dumps({"success": False, "error": "Source and target branches must be different"})

        # Validate source branch belongs to the repository
        source_branch = branches[str(source_branch_id)]
        if str(source_branch.get("repository_id")) != str(repository_id):
            return json.dumps({"success": False, "error": f"Source branch '{source_branch_id}' does not belong to repository '{repository_id}'"})

        # Validate target branch belongs to the repository
        target_branch = branches[str(target_branch_id)]
        if str(target_branch.get("repository_id")) != str(repository_id):
            return json.dumps({"success": False, "error": f"Target branch '{target_branch_id}' does not belong to repository '{repository_id}'"})

        # Validate author exists
        if str(author_id) not in users:
            return json.dumps({"success": False, "error": f"User with id '{author_id}' not found"})

        # Generate new pull_request_id
        if pull_requests:
            max_pr_id = max(int(k) for k in pull_requests.keys())
            new_pr_id = str(max_pr_id + 1)
        else:
            new_pr_id = "1"

        # Create pull request record
        new_pull_request = {
            "pull_request_id": new_pr_id,
            "repository_id": repository_id,
            "pull_request_number": new_pr_id,
            "title": title,
            "description": description,
            "source_branch": source_branch_id,
            "target_branch": target_branch_id,
            "author_id": author_id,
            "status": status,
            "created_at": "2026-01-01T23:59:00",
            "updated_at": "2026-01-01T23:59:00",
            "merged_at": None,
            "closed_at": None,
            "merged_by": None
        }

        pull_requests[new_pr_id] = new_pull_request

        return json.dumps({"success": True, "result": new_pull_request})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "open_pull_request",
                "description": "Opens a new pull request in a repository to merge changes from a source branch into a target branch.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository."
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the pull request."
                        },
                        "source_branch_id": {
                            "type": "string",
                            "description": "The unique identifier of the branch containing the changes to merge."
                        },
                        "target_branch_id": {
                            "type": "string",
                            "description": "The unique identifier of the branch to merge changes into."
                        },
                        "author_id": {
                            "type": "string",
                            "description": "The unique identifier of the user creating the pull request."
                        },
                        "description": {
                            "type": "string",
                            "description": "A detailed description of the changes in the pull request. Optional."
                        },
                        "status": {
                            "type": "string",
                            "description": "The initial status of the pull request. Valid values: open, draft, closed, merged. Default: open."
                        }
                    },
                    "required": ["repository_id", "title", "source_branch_id", "target_branch_id", "author_id"]
                }
            }
        }
