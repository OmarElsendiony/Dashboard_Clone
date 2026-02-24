import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class MergePr(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        pull_request_number: int,
        merged_by: str,
    ) -> str:
        timestamp = "2026-02-02 23:59:00"

        def find_branch_by_name(branches_dict: Dict[str, Any], repository_id_str: str, branch_name_str: str) -> Optional[str]:
            """Find branch ID by repository and branch name."""
            for bid, branch in branches_dict.items():
                if not isinstance(branch, dict):
                    continue
                if (
                    str(branch.get("repository_id")).strip() == repository_id_str
                    and str(branch.get("branch_name", "")).strip() == branch_name_str
                ):
                    return str(bid)
            return None

        def find_pr_by_number(pull_requests_dict: Dict[str, Any], repository_id_str: str, pr_number: int) -> tuple:
            """Find pull request by repository and PR number."""
            for pid, pr in pull_requests_dict.items():
                if not isinstance(pr, dict):
                    continue
                if (
                    str(pr.get("repository_id")).strip() == repository_id_str
                    and int(pr.get("pull_request_number")) == pr_number
                ):
                    return str(pid), pr
            return None, None

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        if not repository_id:
            return json.dumps({"success": False, "error": "Missing required parameter: 'repository_id'"})

        if not pull_request_number:
            return json.dumps({"success": False, "error": "Missing required parameter: 'pull_request_number'"})

        if not merged_by:
            return json.dumps({"success": False, "error": "Missing required parameter: 'merged_by'"})

        repositories_dict = data.get("repositories", {})
        pull_requests_dict = data.get("pull_requests", {})
        branches_dict = data.get("branches", {})
        users_dict = data.get("users", {})

        repository_id_str = str(repository_id).strip()
        pr_number = int(pull_request_number)
        merged_by_str = str(merged_by).strip()

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

        if merged_by_str not in users_dict:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{merged_by_str}' not found"
            })

        merger = users_dict[merged_by_str]

        if not isinstance(merger, dict):
            return json.dumps({
                "success": False,
                "error": f"Invalid user data structure for user ID '{merged_by_str}'"
            })

        merger_status = str(merger.get("status", ""))
        if merger_status != 'active':
            return json.dumps({
                "success": False,
                "error": f"User '{merged_by_str}' is not active and cannot merge pull requests"
            })

        pr_status = str(pull_request.get("status", "")).strip()
        valid_merge_statuses = ["open"]

        if pr_status not in valid_merge_statuses:
            return json.dumps({
                "success": False,
                "error": f"Pull request #{pr_number} has status '{pr_status}' and cannot be merged. Only pull requests with status 'open' can be merged."
            })

        source_branch_name = str(pull_request.get("source_branch_name", "")).strip()
        target_branch_name = str(pull_request.get("target_branch_name", "")).strip()

        if not source_branch_name or not target_branch_name:
            return json.dumps({
                "success": False,
                "error": f"Pull request #{pr_number} is missing source or target branch information"
            })

        source_branch_id = find_branch_by_name(branches_dict, repository_id_str, source_branch_name)
        if not source_branch_id:
            return json.dumps({
                "success": False,
                "error": f"Source branch '{source_branch_name}' not found in repository '{repository_id_str}'"
            })

        target_branch_id = find_branch_by_name(branches_dict, repository_id_str, target_branch_name)
        if not target_branch_id:
            return json.dumps({
                "success": False,
                "error": f"Target branch '{target_branch_name}' not found in repository '{repository_id_str}'"
            })

        linked_ticket_id = pull_request.get("linked_ticket_id")
        if linked_ticket_id:
            tickets_dict = data.get("tickets", {})
            if str(linked_ticket_id) in tickets_dict:
                ticket = tickets_dict[str(linked_ticket_id)]
                if isinstance(ticket, dict):
                    ticket_description = str(ticket.get("description", "")).lower()
                    # Check for security-related keywords
                    security_keywords = ["pii", "credential", "vulnerability", "security breach", "data leak"]
                    if any(keyword in ticket_description for keyword in security_keywords):
                        pr_reviews_dict = data.get("pull_request_reviews", {})
                        has_security_approval = False

                        for _, review in pr_reviews_dict.items():
                            if not isinstance(review, dict):
                                continue
                            if (str(review.get("pull_request_id")) == pull_request_id_str and
                                str(review.get("review_status", "")).strip() == "approved"):
                                reviewer_id = str(review.get("reviewer_id", "")).strip()
                                if reviewer_id in users_dict:
                                    reviewer = users_dict[reviewer_id]
                                    if isinstance(reviewer, dict):
                                        expertise = str(reviewer.get("technical_expertise", "")).strip()
                                        if expertise == "security_specialist":
                                            has_security_approval = True
                                            break

                        if not has_security_approval:
                            return json.dumps({
                                "success": False,
                                "error": f"Pull request #{pr_number} is linked to a security-related ticket and requires security team approval before merge"
                            })

        pull_request["status"] = "merged"
        pull_request["merged_by"] = str(merged_by_str) if merged_by_str else None
        pull_request["merged_at"] = timestamp
        pull_request["updated_at"] = timestamp

        pr_return = pull_request.copy()
        pr_return["pull_request_id"] = str(pull_request_id_str) if pull_request_id_str else None
        pr_return["merger_email"] = str(merger.get("email")) if merger.get("email") else None
        pr_return["merger_name"] = f"{merger.get('first_name', '')} {merger.get('last_name', '')}".strip()
        pr_return["repository_name"] = str(repository.get("repository_name")) if repository.get("repository_name") else None
        pr_return.pop("gate_traceability", None)
        pr_return.pop("gate_ci_status", None)
        pr_return.pop("gate_test_coverage", None)

        message = f"Pull request #{pr_number} merged successfully: '{pull_request.get('title', '')}' (from '{source_branch_name}' to '{target_branch_name}')"

        return json.dumps({
            "success": True,
            "pull_request": pr_return,
            "message": message,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return tool metadata for the merge_pr function."""
        return {
            "type": "function",
            "function": {
                "name": "merge_pr",
                "description": (
                    "Merges an approved pull request, integrating code changes from the source branch into the target branch. "
                    "This function completes the code review process by applying the proposed changes to the destination branch. "
                    "Use this when a pull request has been reviewed and approved, when fixes are ready to be deployed to production, "
                    "or when emergency fixes need to be integrated immediately. "
                    "Note that security-related pull requests require security team approval before merge."
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
                            "description": "The pull request number to merge.",
                        },
                        "merged_by": {
                            "type": "string",
                            "description": "The unique identifier of the user performing the merge.",
                        },
                    },
                    "required": ["repository_id", "pull_request_number", "merged_by"],
                },
            },
        }
