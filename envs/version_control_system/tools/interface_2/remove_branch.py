import json
from typing import Any, Dict, Set
from tau_bench.envs.tool import Tool


class RemoveBranch(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        branch_id: str,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        branches_dict = data.get("branches", {})
        pull_requests_dict = data.get("pull_requests", {})
        pull_request_reviews_dict = data.get("pull_request_reviews", {})
        comments_dict = data.get("comments", {})

        branch_id_str = str(branch_id).strip()

        if branch_id_str not in branches_dict:
            return json.dumps({
                "success": False,
                "error": f"Branch with ID '{branch_id_str}' not found",
            })

        branch_info = branches_dict[branch_id_str].copy()
        repository_id = str(branch_info.get("repository_id"))
        branch_name = str(branch_info.get("branch_name"))

        related_pr_ids: Set[str] = set()
        open_prs = []
        
        for pr_id, pr in pull_requests_dict.items():
            if not isinstance(pr, dict) or str(pr.get("repository_id")) != repository_id:
                continue
            
            pr_source_branch = str(pr.get("source_branch"))
            pr_target_branch = str(pr.get("target_branch"))
            pr_status = str(pr.get("status", "")).lower()
            
            # Check if this branch is involved in the PR
            if pr_source_branch == branch_name or pr_target_branch == branch_name:
                related_pr_ids.add(str(pr_id))
                
                # PR must be merged or closed
                if pr_status not in ["merged", "closed"]:
                    open_prs.append({
                        "pr_id": str(pr_id),
                        "pr_number": pr.get("pull_request_number"),
                        "status": pr_status
                    })

        # If there are open PRs, return error
        if open_prs:
            return json.dumps({
                "success": False,
                "error": f"Cannot delete branch '{branch_name}'. {len(open_prs)} pull request(s) are still open or draft"
            })

        # All PRs are merged or closed, proceed with cascade delete
        for review_id in list(pull_request_reviews_dict.keys()):
            if isinstance(pull_request_reviews_dict[review_id], dict) and str(pull_request_reviews_dict[review_id].get("pull_request_id")) in related_pr_ids:
                del pull_request_reviews_dict[review_id]

        for comment_id in list(comments_dict.keys()):
            comment = comments_dict[comment_id]
            if isinstance(comment, dict):
                commentable_type = str(comment.get("commentable_type", ""))
                commentable_id = str(comment.get("commentable_id", ""))
                if commentable_type == "pull_request" and commentable_id in related_pr_ids:
                    del comments_dict[comment_id]

        for pr_id in related_pr_ids:
            if pr_id in pull_requests_dict:
                del pull_requests_dict[pr_id]

        del branches_dict[branch_id_str]

        return json.dumps({
            "success": True,
            "deleted_branch": branch_info,
            "message": f"Branch '{branch_name}' and {len(related_pr_ids)} related pull request(s) deleted successfully",
            "deleted_counts": {
                "pull_requests": len(related_pr_ids),
            }
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        
        return {
            "type": "function",
            "function": {
                "name": "remove_branch",
                "description": (
                    "Removes a branch after confirming it exists. Check all pull requests where the branch is used as source or target. If any pull request is open or in draft, return an error with the list of those pull requests. If all are merged or closed, delete the branch and all related pull requests, including their reviews and comments, and return the deleted branch details with the count of removed pull requests."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "branch_id": {
                            "type": "string",
                            "description": "The ID of the branch to remove.",
                        },
                    },
                    "required": ["branch_id"],
                },
            },
        }
