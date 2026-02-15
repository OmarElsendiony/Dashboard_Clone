import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreatePr(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        author_id: str,
        title: str,
        source_branch_name: str,
        target_branch_name: str,
        description: Optional[str] = None,
        linked_ticket_id: Optional[str] = None,
    ) -> str:
        timestamp = "2026-02-02 23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            """Generate a new unique ID for a record."""
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        def generate_pr_number(pull_requests_dict: Dict[str, Any], repository_id_str: str) -> int:
            """Generate the next PR number for a repository."""
            max_number = 0
            for pr in pull_requests_dict.values():
                if isinstance(pr, dict) and str(pr.get("repository_id")) == repository_id_str:
                    pr_number = pr.get("pull_request_number", 0)
                    try:
                        max_number = max(max_number, int(pr_number))
                    except (ValueError, TypeError):
                        continue
            return max_number + 1

        def find_branch_by_name(branches_dict: Dict[str, Any], repository_id_str: str, branch_name_str: str) -> Optional[str]:
            """Find branch ID by repository and branch name."""
            for bid, branch in branches_dict.items():
                if not isinstance(branch, dict):
                    continue
                if (str(branch.get("repository_id")) == repository_id_str and
                    str(branch.get("branch_name", "")).strip() == branch_name_str):
                    return str(bid)
            return None

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        if not repository_id:
            return json.dumps({"success": False, "error": "Missing required parameter: 'repository_id'"})

        if not author_id:
            return json.dumps({"success": False, "error": "Missing required parameter: 'author_id'"})

        if not title:
            return json.dumps({"success": False, "error": "Missing required parameter: 'title'"})

        if not source_branch_name:
            return json.dumps({"success": False, "error": "Missing required parameter: 'source_branch_name'"})

        if not target_branch_name:
            return json.dumps({"success": False, "error": "Missing required parameter: 'target_branch_name'"})

        repositories_dict = data.get("repositories", {})
        pull_requests_dict = data.get("pull_requests", {})
        branches_dict = data.get("branches", {})
        users_dict = data.get("users", {})
        tickets_dict = data.get("tickets", {})

        repository_id_str = str(repository_id).strip()
        author_id_str = str(author_id).strip()
        title_str = str(title).strip()
        source_branch_name_str = str(source_branch_name).strip()
        target_branch_name_str = str(target_branch_name).strip()
        description_str = str(description).strip() if description else None
        linked_ticket_id_str = str(linked_ticket_id).strip() if linked_ticket_id else None

        if not title_str:
            return json.dumps({
                "success": False,
                "error": "Pull request title cannot be empty"
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

        if author_id_str not in users_dict:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{author_id_str}' not found"
            })

        author = users_dict[author_id_str]

        if not isinstance(author, dict):
            return json.dumps({
                "success": False,
                "error": f"Invalid user data structure for author ID '{author_id_str}'"
            })

        author_status = author.get("status")
        if author_status != 'active':
            return json.dumps({
                "success": False,
                "error": f"User '{author_id_str}' is not active and cannot create pull requests"
            })

        source_branch_id = find_branch_by_name(branches_dict, repository_id_str, source_branch_name_str)
        if not source_branch_id:
            return json.dumps({
                "success": False,
                "error": f"Source branch '{source_branch_name_str}' not found in repository '{repository_id_str}'"
            })

        source_branch = branches_dict[source_branch_id]

        source_branch_status = str(source_branch.get("status", "")).strip()
        if source_branch_status != "active":
            return json.dumps({
                "success": False,
                "error": f"Source branch '{source_branch_name_str}' has status '{source_branch_status}' and cannot be used for pull requests"
            })

        target_branch_id = find_branch_by_name(branches_dict, repository_id_str, target_branch_name_str)
        if not target_branch_id:
            return json.dumps({
                "success": False,
                "error": f"Target branch '{target_branch_name_str}' not found in repository '{repository_id_str}'"
            })

        target_branch = branches_dict[target_branch_id]

        target_branch_status = str(target_branch.get("status", "")).strip()
        if target_branch_status != "active":
            return json.dumps({
                "success": False,
                "error": f"Target branch '{target_branch_name_str}' has status '{target_branch_status}' and cannot be used as target for pull requests"
            })

        if source_branch_name_str == target_branch_name_str:
            return json.dumps({
                "success": False,
                "error": "Source and target branches cannot be the same"
            })

        if linked_ticket_id_str:
            if linked_ticket_id_str not in tickets_dict:
                return json.dumps({
                    "success": False,
                    "error": f"Ticket with ID '{linked_ticket_id_str}' not found"
                })

            ticket = tickets_dict[linked_ticket_id_str]

            if not isinstance(ticket, dict):
                return json.dumps({
                    "success": False,
                    "error": f"Invalid ticket data structure for ticket ID '{linked_ticket_id_str}'"
                })

        for _, pr in pull_requests_dict.items():
            if not isinstance(pr, dict):
                continue
            if (str(pr.get("repository_id")) == repository_id_str and
                str(pr.get("source_branch_name", "")).strip() == source_branch_name_str and
                str(pr.get("target_branch_name", "")).strip() == target_branch_name_str and
                str(pr.get("status", "")).strip() in ["open", "draft"]):
                return json.dumps({
                    "success": False,
                    "error": f"An open pull request already exists from '{source_branch_name_str}' to '{target_branch_name_str}' in repository '{repository_id_str}' (PR #{pr.get('pull_request_number')})"
                })

        new_pr_id = generate_id(pull_requests_dict)
        pr_number = generate_pr_number(pull_requests_dict, repository_id_str)

        new_pull_request = {
            "pull_request_id": new_pr_id,
            "repository_id": repository_id_str,
            "pull_request_number": int(pr_number),
            "title": title_str,
            "description": description_str,
            "source_branch_name": source_branch_name_str,
            "target_branch_name": target_branch_name_str,
            "author_id": author_id_str,
            "status": "open",
            "linked_ticket_id": linked_ticket_id_str,
            "gate_traceability": False,
            "gate_test_coverage": False,
            "gate_ci_status": None,
            "is_emergency_fix": False,
            "assigned_team_lead": None,
            "merged_by": None,
            "merged_at": None,
            "closed_at": None,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        pull_requests_dict[new_pr_id] = new_pull_request

        pr_return = new_pull_request.copy()
        pr_return["author_email"] = author.get("email")
        pr_return["author_name"] = f"{author.get('first_name', '')} {author.get('last_name', '')}".strip()
        pr_return["repository_name"] = repository.get("repository_name")
        pr_return.pop("gate_ci_status", None)
        pr_return.pop("gate_test_coverage", None)
        pr_return.pop("gate_traceability", None)

        message = f"Pull request #{pr_number} created successfully: '{title_str}' (from '{source_branch_name_str}' to '{target_branch_name_str}')"

        return json.dumps({
            "success": True,
            "pull_request": pr_return,
            "message": message,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_pr",
                "description": (
                    "Creates a new pull request to merge code changes from one branch into another. "
                    "This function initiates the code review process by proposing changes from a source branch "
                    "to be merged into a target branch. "
                    "Use this when code fixes or features are ready for review, when proposing solutions to identified issues, "
                    "to link code changes and deployment."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository where the pull request will be created.",
                        },
                        "author_id": {
                            "type": "string",
                            "description": "The unique identifier of the user creating the pull request.",
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the pull request summarizing the changes.",
                        },
                        "source_branch_name": {
                            "type": "string",
                            "description": "The name of the branch containing the changes to be merged.",
                        },
                        "target_branch_name": {
                            "type": "string",
                            "description": "The name of the branch that will receive the changes (typically 'main' or 'master').",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional. Detailed description of the changes, including root cause, fix details, and testing notes.",
                        },
                        "linked_ticket_id": {
                            "type": "string",
                            "description": "Optional. The ID of the support ticket associated with this pull request for traceability.",
                        },
                    },
                    "required": ["repository_id", "author_id", "title", "source_branch_name", "target_branch_name"],
                },
            },
        }
