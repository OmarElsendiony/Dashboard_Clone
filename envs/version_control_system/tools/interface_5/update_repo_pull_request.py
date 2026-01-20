import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdateRepoPullRequest(Tool):
 
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repo_id: str,
        pull_request_number: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
     

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        repositories = data.get("repositories", {})
        pull_requests = data.get("pull_requests", {})

        # Validate repo_id
        if not repo_id:
            return json.dumps({"success": False, "error": "Missing required parameter: repo_id"})

        repo_id = str(repo_id).strip()

        if not repo_id:
            return json.dumps({"success": False, "error": "repo_id cannot be empty"})

        # Validate pull_request_number
        if pull_request_number is None:
            return json.dumps({"success": False, "error": "Missing required parameter: pull_request_number"})

        try:
            pull_request_number = int(pull_request_number)
        except (ValueError, TypeError):
            return json.dumps({"success": False, "error": "pull_request_number must be an integer"})

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

        # Find the pull request by repository_id and pull_request_number
        found_pr = None
        for _, pr in pull_requests.items():
            if (
                str(pr.get("repository_id")) == repo_id
                and pr.get("pull_request_number") == pull_request_number
            ):
                found_pr = pr
                break

        if not found_pr:
            return json.dumps({
                "success": False,
                "error": f"Pull request with number '{pull_request_number}' not found in repository '{repo_id}'"
            })

        # Check if pull request is already closed or merged
        current_status = found_pr.get("status")
        if current_status in {"closed", "merged"}:
            return json.dumps({
                "success": False,
                "error": f"Cannot update pull request #{pull_request_number}: it is already {current_status}"
            })

        # Track if any updates were made
        updates_applied = False

        # Validate and apply title update
        if title is not None:
            if not isinstance(title, str) or not title.strip():
                return json.dumps({"success": False, "error": "title must be a non-empty string"})
            found_pr["title"] = title.strip()
            updates_applied = True

        # Validate and apply description update
        if description is not None:
            if not isinstance(description, str):
                return json.dumps({"success": False, "error": "description must be a string"})
            found_pr["description"] = description.strip()
            updates_applied = True

        # Validate and apply status update
        if status is not None:
            allowed_statuses = {"closed"}
            if not isinstance(status, str):
                return json.dumps({"success": False, "error": "status must be a string"})
            status_val = status.strip().lower()
            if status_val not in allowed_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"status must be one of: {', '.join(sorted(allowed_statuses))}"
                })

            # Handle closed_at timestamp when closing
            timestamp = "2026-01-01T23:59:00"
            if status_val == "closed":
                found_pr["closed_at"] = timestamp

            found_pr["status"] = status_val
            updates_applied = True

        if not updates_applied:
            return json.dumps({
                "success": False,
                "error": "No valid fields supplied for update"
            })

        # Update the updated_at timestamp
        timestamp = "2026-01-01T23:59:00"
        found_pr["updated_at"] = timestamp

        return json.dumps({
            "success": True,
            "message": f"Pull request #{pull_request_number} updated successfully in repository '{repo.get('repository_name')}'",
            "pull_request_data": found_pr
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
       
        return {
            "type": "function",
            "function": {
                "name": "update_repo_pull_request",
                "description": "Updates an existing pull request in a repository. Supports partial updates.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_id": {
                            "type": "string",
                            "description": "The ID of the repository containing the pull request.",
                        },
                        "pull_request_number": {
                            "type": "integer",
                            "description": "The pull request number within the repository.",
                        },
                        "title": {
                            "type": "string",
                            "description": "The new title of the pull request.",
                        },
                        "description": {
                            "type": "string",
                            "description": "The new description of the pull request.",
                        },
                        "status": {
                            "type": "string",
                            "description": "The new status of the pull request.",
                             "enum": ["closed"]
                        },
                    },
                    "required": ["repo_id", "pull_request_number"],
                },
            },
        }
