import json
from typing import Any, Dict, Set
from tau_bench.envs.tool import Tool


class DiscardRepository(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
    ) -> str:
        """Delete a repository and cascade delete all related entities."""

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        repositories_dict = data.get("repositories", {})
        repository_collaborators_dict = data.get("repository_collaborators", {})
        branches_dict = data.get("branches", {})
        commits_dict = data.get("commits", {})
        files_dict = data.get("files", {})
        file_contents_dict = data.get("file_contents", {})
        directories_dict = data.get("directories", {})
        pull_requests_dict = data.get("pull_requests", {})
        pull_request_reviews_dict = data.get("pull_request_reviews", {})
        comments_dict = data.get("comments", {})

        repository_id_str = str(repository_id).strip()

        repository_info = repositories_dict[repository_id_str].copy()

        # Collect pull request IDs from repository
        pull_request_ids: Set[str] = set()
        for pr_id, pr in pull_requests_dict.items():
            if str(pr.get("repository_id")) == repository_id_str:
                pull_request_ids.add(str(pr_id))

        # Collect file IDs from repository
        file_ids: Set[str] = set()
        for file_id, file in files_dict.items():
            if str(file.get("repository_id")) == repository_id_str:
                file_ids.add(str(file_id))
        # Delete cascade - order matters for referential integrity

        # Delete file contents
        for content_id in list(file_contents_dict.keys()):
            if str(file_contents_dict[content_id].get("file_id")) in file_ids:
                del file_contents_dict[content_id]

        # Delete files
        for file_id in file_ids:
            if file_id in files_dict:
                del files_dict[file_id]

        # Delete directories
        for dir_id in list(directories_dict.keys()):
            if str(directories_dict[dir_id].get("repository_id")) == repository_id_str:
                del directories_dict[dir_id]

        # Delete pull request reviews
        for review_id in list(pull_request_reviews_dict.keys()):
            if str(pull_request_reviews_dict[review_id].get("pull_request_id")) in pull_request_ids:
                del pull_request_reviews_dict[review_id]

        # Delete comments
        for comment_id in list(comments_dict.keys()):
            comment = comments_dict[comment_id]
            commentable_type = str(comment.get("commentable_type", ""))
            commentable_id = str(comment.get("commentable_id", ""))
            if (commentable_type == "pull_request" and commentable_id in pull_request_ids):
                del comments_dict[comment_id]

        # Delete pull requests
        for pr_id in pull_request_ids:
            if pr_id in pull_requests_dict:
                del pull_requests_dict[pr_id]
    
        # Delete commits
        for commit_id in list(commits_dict.keys()):
            if str(commits_dict[commit_id].get("repository_id")) == repository_id_str:
                del commits_dict[commit_id]

        # Delete branches
        for branch_id in list(branches_dict.keys()):
            if str(branches_dict[branch_id].get("repository_id")) == repository_id_str:
                del branches_dict[branch_id]

        # Delete repository collaborators
        for collab_id in list(repository_collaborators_dict.keys()):
            if str(repository_collaborators_dict[collab_id].get("repository_id")) == repository_id_str:
                del repository_collaborators_dict[collab_id]

        # Delete repository
        del repositories_dict[repository_id_str]

        return json.dumps({
            "success": True,
            "deleted_repository": repository_info,
            "message": f"Repository '{repository_info.get('repository_name')}' and all related entities deleted successfully",
            "deleted_counts": {
                "pull_requests": len(pull_request_ids),
                "files": len(file_ids),
            }
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return tool metadata for the discard_repository function."""
        return {
            "type": "function",
            "function": {
                "name": "discard_repository",
                "description": "Delete a repository and all related entities.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The ID of the repository to delete.",
                        },
                    },
                    "required": ["repository_id"],
                },
            },
        }
