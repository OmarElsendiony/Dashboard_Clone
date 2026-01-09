import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateRepoPullRequest(Tool):
    """Tool for creating a new pull request in a repository in the version control system."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repo_id: str,
        title: str,
        source_branch: str,
        target_branch: str,
        actor_id: str,
        status: str,
        description: Optional[str] = None,
    ) -> str:
        """
        Create a new pull request in a repository.

        Args:
            data: The data dictionary containing all version control system data.
            repo_id: The ID of the repository to create the pull request in (required).
            title: The title of the pull request (required).
            source_branch: The name of the source branch (required).
            target_branch: The name of the target branch (required).
            actor_id: The ID of the user creating the pull request (required).
            status: The status of the pull request (required, must be 'draft' or 'open').
            description: The description of the pull request (optional).

        Returns:
            str: A JSON-encoded string containing the success status and created pull request data.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            """
            Generates a new unique ID for a record.

            Returns:
                str: The new unique ID as a string.
            """
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        def get_next_pr_number(pull_requests: Dict[str, Any], repo_id: str) -> int:
            """
            Gets the next pull request number for a repository.

            Returns:
                int: The next pull request number.
            """
            max_number = 0
            for _, pr in pull_requests.items():
                if str(pr.get("repository_id")) == repo_id:
                    pr_number = pr.get("pull_request_number", 0)
                    if pr_number > max_number:
                        max_number = pr_number
            return max_number + 1

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        repositories = data.get("repositories", {})
        users = data.get("users", {})
        branches = data.get("branches", {})
        pull_requests = data.get("pull_requests", {})

        # Validate required fields
        if not repo_id:
            return json.dumps({"success": False, "error": "Missing required parameter: repo_id"})

        if not title:
            return json.dumps({"success": False, "error": "Missing required parameter: title"})

        if not isinstance(title, str) or not title.strip():
            return json.dumps({"success": False, "error": "title must be a non-empty string"})

        if not source_branch:
            return json.dumps({"success": False, "error": "Missing required parameter: source_branch"})

        if not isinstance(source_branch, str) or not source_branch.strip():
            return json.dumps({"success": False, "error": "source_branch must be a non-empty string"})

        if not target_branch:
            return json.dumps({"success": False, "error": "Missing required parameter: target_branch"})

        if not isinstance(target_branch, str) or not target_branch.strip():
            return json.dumps({"success": False, "error": "target_branch must be a non-empty string"})

        if not actor_id:
            return json.dumps({"success": False, "error": "Missing required parameter: actor_id"})

        if not status:
            return json.dumps({"success": False, "error": "Missing required parameter: status"})

        # Normalize inputs
        title = title.strip()
        source_branch = source_branch.strip()
        target_branch = target_branch.strip()
        repo_id = str(repo_id).strip()
        actor_id = str(actor_id).strip()

        # Validate status
        allowed_statuses = {"draft", "open"}
        status = status.strip().lower() if isinstance(status, str) else ""
        if status not in allowed_statuses:
            return json.dumps({
                "success": False,
                "error": f"status must be one of: {', '.join(sorted(allowed_statuses))}"
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
                "error": f"Cannot create pull request in archived repository '{repo.get('repository_name')}'"
            })

        # Validate author exists
        if actor_id not in users:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{actor_id}' not found"
            })

        author = users[actor_id]

        # Check if author is active
        if author.get("status") != "active":
            return json.dumps({
                "success": False,
                "error": f"User '{actor_id}' is not active"
            })

        # Validate source branch exists
        source_branch_found = False
        for _, branch in branches.items():
            if (
                str(branch.get("repository_id")) == repo_id
                and branch.get("branch_name") == source_branch
            ):
                source_branch_found = True
                break

        if not source_branch_found:
            return json.dumps({
                "success": False,
                "error": f"Source branch '{source_branch}' not found in repository '{repo.get('repository_name')}'"
            })

        # Validate target branch exists
        target_branch_found = False
        for _, branch in branches.items():
            if (
                str(branch.get("repository_id")) == repo_id
                and branch.get("branch_name") == target_branch
            ):
                target_branch_found = True
                break

        if not target_branch_found:
            return json.dumps({
                "success": False,
                "error": f"Target branch '{target_branch}' not found in repository '{repo.get('repository_name')}'"
            })

        # Validate source and target branches are different
        if source_branch == target_branch:
            return json.dumps({
                "success": False,
                "error": "Source branch and target branch must be different"
            })

        # Check for existing open/draft PR with same source and target branches
        for _, pr in pull_requests.items():
            if (
                str(pr.get("repository_id")) == repo_id
                and pr.get("source_branch") == source_branch
                and pr.get("target_branch") == target_branch
                and pr.get("status") in {"open", "draft"}
            ):
                return json.dumps({
                    "success": False,
                    "error": f"An open or draft pull request already exists from '{source_branch}' to '{target_branch}'"
                })

        # Set timestamp for created_at and updated_at
        timestamp = "2026-01-01T23:59:00"

        # Generate new pull request ID and number
        new_pr_id = generate_id(pull_requests)
        new_pr_number = get_next_pr_number(pull_requests, repo_id)

        # Process description
        description_value = description.strip() if isinstance(description, str) and description.strip() else ""

        # Create new pull request record
        new_pr = {
            "pull_request_id": new_pr_id,
            "repository_id": repo_id,
            "pull_request_number": new_pr_number,
            "title": title,
            "description": description_value,
            "author_id": actor_id,
            "source_branch": source_branch,
            "target_branch": target_branch,
            "status": status,
            "merged_by": None,
            "merged_at": None,
            "closed_at": None,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        # Add the new pull request to the pull_requests dictionary
        pull_requests[new_pr_id] = new_pr

        return json.dumps({
            "success": True,
            "message": f"Pull request #{new_pr_number} created successfully in repository '{repo.get('repository_name')}'",
            "pull_request_data": new_pr
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return the tool specification for the create_repo_pull_request function."""
        return {
            "type": "function",
            "function": {
                "name": "create_repo_pull_request",
                "description": "Create a new pull request to propose merging changes from one branch into another. The pull request can be created as a draft or open for review.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_id": {
                            "type": "string",
                            "description": "The ID of the repository.",
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the pull request.",
                        },
                        "source_branch": {
                            "type": "string",
                            "description": "The name of the branch containing the changes to merge.",
                        },
                        "target_branch": {
                            "type": "string",
                            "description": "The name of the branch to merge changes into.",
                        },
                        "actor_id": {
                            "type": "string",
                            "description": "The ID of the user creating the pull request.",
                        },
                        "status": {
                            "type": "string",
                            "description": "The initial status; one of draft or open.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional description of the pull request.",
                        },
                    },
                    "required": ["repo_id", "title", "source_branch", "target_branch", "actor_id", "status"],
                },
            },
        }
