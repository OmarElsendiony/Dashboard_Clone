import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class CreatePrComment(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        pull_request_number: int,
        author_id: str,
        comment_body: str,
    ) -> str:
        timestamp = "2026-02-02 23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        def find_pr_by_number(pull_requests_dict: Dict[str, Any], repository_id_str: str, pr_number: int) -> tuple:
            for pid, pr in pull_requests_dict.items():
                if not isinstance(pr, dict):
                    continue
                if (str(pr.get("repository_id")) == repository_id_str and
                    pr.get("pull_request_number") == pr_number):
                    return str(pid), pr
            return None, None

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        if not repository_id:
            return json.dumps({"success": False, "error": "Missing required parameter: 'repository_id'"})

        if not pull_request_number:
            return json.dumps({"success": False, "error": "Missing required parameter: 'pull_request_number'"})

        if not author_id:
            return json.dumps({"success": False, "error": "Missing required parameter: 'author_id'"})

        if not comment_body:
            return json.dumps({"success": False, "error": "Missing required parameter: 'comment_body'"})

        repositories_dict = data.get("repositories", {})
        pull_requests_dict = data.get("pull_requests", {})
        pull_request_comments_dict = data.get("pull_request_comments", {})
        users_dict = data.get("users", {})

        repository_id_str = str(repository_id).strip()
        pr_number = int(pull_request_number)
        author_id_str = str(author_id).strip()
        comment_body_str = str(comment_body).strip()

        if not comment_body_str:
            return json.dumps({
                "success": False,
                "error": "Comment body cannot be empty"
            })

        if repository_id_str not in repositories_dict:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repository_id_str}' not found"
            })

        repository = repositories_dict[repository_id_str]

        if not isinstance(repository, dict):
            return json.dumps({
                "success": False,
                "error": f"Invalid repository data structure for repository ID '{repository_id_str}'"
            })

        pull_request_id_str, pull_request = find_pr_by_number(pull_requests_dict, repository_id_str, pr_number)

        if not pull_request_id_str or not pull_request:
            return json.dumps({
                "success": False,
                "error": f"Pull request #{pr_number} not found in repository '{repository_id_str}'"
            })

        pr_status = str(pull_request.get("status", "")).strip()
        valid_comment_statuses = ["draft", "open"]

        if pr_status not in valid_comment_statuses:
            return json.dumps({
                "success": False,
                "error": f"Pull request #{pr_number} has status '{pr_status}' and cannot receive comments. Only pull requests with status 'draft' or 'open' can be commented on."
            })

        if author_id_str not in users_dict:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{author_id_str}' not found"
            })

        author = users_dict[author_id_str]

        if not isinstance(author, dict):
            return json.dumps({
                "success": False,
                "error": f"Invalid user data structure for user ID '{author_id_str}'"
            })

        author_status = author.get("status")
        if author_status != 'active':
            return json.dumps({
                "success": False,
                "error": f"User '{author_id_str}' is not active and cannot create comments"
            })

        new_comment_id = generate_id(pull_request_comments_dict)
        new_comment = {
            "comment_id": str(new_comment_id) if new_comment_id else None,
            "pull_request_id": str(pull_request_id_str) if pull_request_id_str else None,
            "author_id": str(author_id_str) if author_id_str else None,
            "comment_body": str(comment_body_str) if comment_body_str else None,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        pull_request_comments_dict[new_comment_id] = new_comment

        pull_request["updated_at"] = timestamp

        comment_return = new_comment.copy()
        comment_return["author_email"] = str(author.get("email")) if author.get("email") else None
        comment_return["author_name"] = str(f"{author.get('first_name', '')} {author.get('last_name', '')}".strip())
        comment_return["pull_request_title"] = str(pull_request.get("title")) if pull_request.get("title") else None
        comment_return["pull_request_number"] = int(pr_number) if pr_number else None
        comment_return["repository_name"] = str(repository.get("repository_name")) if repository.get("repository_name") else None

        message = f"Comment added to pull request #{pr_number}: '{pull_request.get('title', '')}'"

        return json.dumps({
            "success": True,
            "comment": comment_return,
            "message": message,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_pr_comment",
                "description": (
                    "Adds a comment to a pull request for discussion, feedback, or documentation purposes. "
                    "This function enables communication between team members regarding proposed code changes. "
                    "Use this when providing feedback on code modifications, documenting security concerns, "
                    "adding priority flags for critical fixes, or facilitating collaborative review discussions."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository containing the pull request.",
                        },
                        "pull_request_number": {
                            "type": "integer",
                            "description": "The pull request number to comment on.",
                        },
                        "author_id": {
                            "type": "string",
                            "description": "The unique identifier of the user creating the comment.",
                        },
                        "comment_body": {
                            "type": "string",
                            "description": "The content of the comment to add to the pull request.",
                        },
                    },
                    "required": ["repository_id", "pull_request_number", "author_id", "comment_body"],
                },
            },
        }
