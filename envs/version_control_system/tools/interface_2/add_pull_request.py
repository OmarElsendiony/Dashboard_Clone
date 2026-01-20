import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class AddPullRequest(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        title: str,
        author_id: str,
        source_branch: str,
        target_branch: str,
        description: Optional[str] = None,
    ) -> str:
        """Create a new pull request."""
        timestamp = "2026-01-01T23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            """Generate a new unique ID for a record."""
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        def get_next_pr_number(pull_requests_dict: Dict[str, Any], repository_id_str: str) -> int:
            """ Get the next pull request number for the repository."""
            max_number = 0
            for pr in pull_requests_dict.values():
                if str(pr.get("repository_id")) == repository_id_str:
                    max_number = max(max_number, int(pr.get("pull_request_number", 0)))
            return max_number + 1

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        pull_requests_dict = data.get("pull_requests", {})

        repository_id_str = str(repository_id).strip()
        title_str = str(title).strip()
        author_id_str = str(author_id).strip()
        source_branch_str = str(source_branch).strip()
        target_branch_str = str(target_branch).strip()
        description_str = str(description).strip() if description else None


        # Generate new pull request ID and number
        new_pr_id = generate_id(pull_requests_dict)
        pr_number = get_next_pr_number(pull_requests_dict, repository_id_str)

        # Create new pull request
        new_pull_request = {
            "pull_request_id": new_pr_id,
            "repository_id": repository_id_str,
            "pull_request_number": int(pr_number),
            "title": title_str,
            "description": description_str,
            "author_id": author_id_str,
            "source_branch": source_branch_str,
            "target_branch": target_branch_str,
            "status": "open",
            "merged_by": None,
            "merged_at": None,
            "closed_at": None,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        pull_requests_dict[new_pr_id] = new_pull_request

        return json.dumps({
            "success": True,
            "pull_request": new_pull_request,
            "message": f"Pull request #{pr_number} '{title_str}' created successfully in repository '{repository_id_str}'",
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return tool metadata for the add_pull_request function."""
        return {
            "type": "function",
            "function": {
                "name": "add_pull_request",
                "description": "Creates a new pull request in a repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The ID of the repository where the pull request will be created.",
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the pull request.",
                        },
                        "author_id": {
                            "type": "string",
                            "description": "The ID of the user creating the pull request.",
                        },
                        "source_branch": {
                            "type": "string",
                            "description": "The name of the source branch (branch to merge from).",
                        },
                        "target_branch": {
                            "type": "string",
                            "description": "The name of the target branch (branch to merge into).",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional. The description of the pull request.",
                        },
                    },
                    "required": ["repository_id", "title", "author_id", "source_branch", "target_branch"],
                },
            },
        }
