import json
from typing import Any, Dict, Set
from tau_bench.envs.tool import Tool


class DeleteProject(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        project_id: str,
    ) -> str:

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        # Get data containers
        projects_dict = data.get("projects", {})
        project_members_dict = data.get("project_members", {})
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

        project_id_str = str(project_id).strip()
        project_info = projects_dict[project_id_str].copy()

        if project_id_str not in projects_dict:
            return json.dumps({
                "success": False,
                "error": f"Project with id {project_id_str} not found"
            })

        # Collect repository IDs in the project
        repository_ids: Set[str] = set()
        for repo_id, repo in repositories_dict.items():
            if str(repo.get("project_id")) == project_id_str:
                repository_ids.add(str(repo_id))

        # Collect pull request IDs from repositories
        pull_request_ids: Set[str] = set()
        for pr_id, pr in pull_requests_dict.items():
            if str(pr.get("repository_id")) in repository_ids:
                pull_request_ids.add(str(pr_id))

        # Collect file IDs from repositories
        file_ids: Set[str] = set()
        for file_id, file in files_dict.items():
            if str(file.get("repository_id")) in repository_ids:
                file_ids.add(str(file_id))
        
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
            if str(directories_dict[dir_id].get("repository_id")) in repository_ids:
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
            if str(commits_dict[commit_id].get("repository_id")) in repository_ids:
                del commits_dict[commit_id]

        # Delete branches
        for branch_id in list(branches_dict.keys()):
            if str(branches_dict[branch_id].get("repository_id")) in repository_ids:
                del branches_dict[branch_id]

        # Delete repository collaborators
        for collab_id in list(repository_collaborators_dict.keys()):
            if str(repository_collaborators_dict[collab_id].get("repository_id")) in repository_ids:
                del repository_collaborators_dict[collab_id]

        # Delete repositories
        for repo_id in repository_ids:
            if repo_id in repositories_dict:
                del repositories_dict[repo_id]

        # Delete project members
        for pm_id in list(project_members_dict.keys()):
            if str(project_members_dict[pm_id].get("project_id")) == project_id_str:
                del project_members_dict[pm_id]

        # Delete project
        del projects_dict[project_id_str]

        return json.dumps({
            "success": True,
            "deleted_project": project_info,
            "message": f"Project '{project_info.get('project_name')}' and all related entities deleted successfully",
            "deleted_counts": {
                "repositories": len(repository_ids),
                "pull_requests": len(pull_request_ids),
                "files": len(file_ids),
            }
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        
        return {
            "type": "function",
            "function": {
                "name": "delete_project",
                "description": (
                    "Deletes a project after validating it exists. Removes the project and all related data. Returns information about the deleted project details with counts of removed items."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The ID of the project to delete.",
                        },
                    },
                    "required": ["project_id"],
                },
            },
        }
