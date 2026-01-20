import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class RemoveRepository(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not repository_id:
            return json.dumps({"success": False, "error": "repository_id is required to remove repository"})

        repositories = data.get("repositories", {})

        # Validate repository exists
        if str(repository_id) not in repositories:
            return json.dumps({"success": False, "error": f"Repository with id '{repository_id}' not found"})

        repo = repositories[str(repository_id)]

        # Cascade delete all related entities

        # Delete repository collaborators
        repository_collaborators = data.get("repository_collaborators", {})
        collab_ids_to_delete = [
            cid for cid, collab in repository_collaborators.items()
            if str(collab.get("repository_id")) == str(repository_id)
        ]
        for cid in collab_ids_to_delete:
            del repository_collaborators[cid]

        # Delete branches
        branches = data.get("branches", {})
        branch_ids_to_delete = [
            bid for bid, branch in branches.items()
            if str(branch.get("repository_id")) == str(repository_id)
        ]
        for bid in branch_ids_to_delete:
            del branches[bid]

        # Delete commits
        commits = data.get("commits", {})
        commit_ids_to_delete = [
            cid for cid, commit in commits.items()
            if str(commit.get("repository_id")) == str(repository_id)
        ]
        for cid in commit_ids_to_delete:
            del commits[cid]

        # Delete directories
        directories = data.get("directories", {})
        dir_ids_to_delete = [
            did for did, directory in directories.items()
            if str(directory.get("repository_id")) == str(repository_id)
        ]
        for did in dir_ids_to_delete:
            del directories[did]

        # Delete files and their contents
        files = data.get("files", {})
        file_contents = data.get("file_contents", {})
        file_ids_to_delete = [
            fid for fid, file in files.items()
            if str(file.get("repository_id")) == str(repository_id)
        ]
        # Delete file contents first
        content_ids_to_delete = [
            fcid for fcid, fc in file_contents.items()
            if str(fc.get("file_id")) in file_ids_to_delete
        ]
        for fcid in content_ids_to_delete:
            del file_contents[fcid]
        # Then delete files
        for fid in file_ids_to_delete:
            del files[fid]

        # Delete pull requests and their reviews/comments
        pull_requests = data.get("pull_requests", {})
        pull_request_reviews = data.get("pull_request_reviews", {})
        code_reviews = data.get("code_reviews", {})
        comments = data.get("comments", {})

        pr_ids_to_delete = [
            prid for prid, pr in pull_requests.items()
            if str(pr.get("repository_id")) == str(repository_id)
        ]
        # Delete PR reviews
        pr_review_ids_to_delete = [
            rid for rid, review in pull_request_reviews.items()
            if str(review.get("pull_request_id")) in pr_ids_to_delete
        ]
        for rid in pr_review_ids_to_delete:
            del pull_request_reviews[rid]
        # Delete code reviews
        code_review_ids_to_delete = [
            rid for rid, review in code_reviews.items()
            if str(review.get("pull_request_id")) in pr_ids_to_delete
        ]
        for rid in code_review_ids_to_delete:
            del code_reviews[rid]
        # Delete PR comments
        pr_comment_ids_to_delete = [
            cid for cid, comment in comments.items()
            if str(comment.get("pull_request_id")) in pr_ids_to_delete
        ]
        for cid in pr_comment_ids_to_delete:
            del comments[cid]
        # Delete pull requests
        for prid in pr_ids_to_delete:
            del pull_requests[prid]

        # Delete issues and their comments
        issues = data.get("issues", {})
        issue_ids_to_delete = [
            iid for iid, issue in issues.items()
            if str(issue.get("repository_id")) == str(repository_id)
        ]
        # Delete issue comments
        issue_comment_ids_to_delete = [
            cid for cid, comment in comments.items()
            if str(comment.get("issue_id")) in issue_ids_to_delete
        ]
        for cid in issue_comment_ids_to_delete:
            del comments[cid]
        # Delete issues
        for iid in issue_ids_to_delete:
            del issues[iid]

        # Delete labels associated with the repository
        labels = data.get("labels", {})
        label_ids_to_delete = [
            lid for lid, label in labels.items()
            if str(label.get("repository_id")) == str(repository_id)
        ]
        for lid in label_ids_to_delete:
            del labels[lid]

        # Delete workflows
        workflows = data.get("workflows", {})
        workflow_ids_to_delete = [
            wid for wid, workflow in workflows.items()
            if str(workflow.get("repository_id")) == str(repository_id)
        ]
        for wid in workflow_ids_to_delete:
            del workflows[wid]

        # Delete releases
        releases = data.get("releases", {})
        release_ids_to_delete = [
            rid for rid, release in releases.items()
            if str(release.get("repository_id")) == str(repository_id)
        ]
        for rid in release_ids_to_delete:
            del releases[rid]

        # Delete stars
        stars = data.get("stars", {})
        star_ids_to_delete = [
            sid for sid, star in stars.items()
            if str(star.get("repository_id")) == str(repository_id)
        ]
        for sid in star_ids_to_delete:
            del stars[sid]

        # Delete notifications related to the repository
        notifications = data.get("notifications", {})
        notification_ids_to_delete = [
            nid for nid, notification in notifications.items()
            if str(notification.get("repository_id")) == str(repository_id)
        ]
        for nid in notification_ids_to_delete:
            del notifications[nid]

        # Finally, delete the repository
        deleted_repo = repositories.pop(str(repository_id))

        return json.dumps({
            "success": True,
            "result": deleted_repo,
            "message": f"Repository '{deleted_repo.get('repository_name')}' has been deleted along with {len(branch_ids_to_delete)} branches, {len(commit_ids_to_delete)} commits, {len(file_ids_to_delete)} files, {len(pr_ids_to_delete)} pull requests, {len(issue_ids_to_delete)} issues, and {len(collab_ids_to_delete)} collaborators"
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "remove_repository",
                "description": "Permanently deletes a repository and all its associated data from the version control system.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository to delete."
                        }
                    },
                    "required": ["repository_id"]
                }
            }
        }
