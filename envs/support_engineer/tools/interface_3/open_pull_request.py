import json
from typing import Dict, Optional, Any
from tau_bench.envs.tool import Tool


class OpenPullRequest(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_name: str,
        title: str,
        source_branch_name: str,
        author_id: str,
        target_branch_name: str = "main",
        description: Optional[str] = None,
        status: str = "open",
        linked_ticket_id: Optional[str] = None,
    ) -> str:
        pull_requests = data.get("pull_requests", {})
        repositories = data.get("repositories", {})
        branches = data.get("branches", {})
        users = data.get("users", {})
        timestamp = "2026-02-02 23:59:00"

        if not repository_name:
            return json.dumps({"error": "repository_name is required"})

        if not title:
            return json.dumps({"error": "title is required"})

        if not source_branch_name:
            return json.dumps({"error": "source_branch_name is required"})

        if not author_id:
            return json.dumps({"error": "author_id is required"})

        if status not in ("draft", "open"):
            return json.dumps(
                {"error": f"Invalid status '{status}'. Must be 'draft' or 'open'"}
            )

        repo = None
        for r in repositories.values():
            if r.get("repository_name") == repository_name:
                repo = r
                break
        if not repo:
            return json.dumps(
                {"error": f"Repository with name '{repository_name}' not found"}
            )

        repository_id = str(repo["repository_id"])

        author = users.get(str(author_id))
        if not author:
            return json.dumps({"error": f"User with ID '{author_id}' not found"})

        source_exists = False
        for branch in branches.values():
            if (str(branch.get("repository_id")) == repository_id
                    and branch.get("branch_name") == source_branch_name):
                source_exists = True
                break
        if not source_exists:
            return json.dumps(
                {"error": f"Source branch '{source_branch_name}' not found in repository '{repository_name}'"}
            )

        target_exists = False
        for branch in branches.values():
            if (str(branch.get("repository_id")) == repository_id
                    and branch.get("branch_name") == target_branch_name):
                target_exists = True
                break
        if not target_exists:
            return json.dumps(
                {"error": f"Target branch '{target_branch_name}' not found in repository '{repository_name}'"}
            )

        if source_branch_name == target_branch_name:
            return json.dumps(
                {"error": "Source branch and target branch cannot be the same"}
            )

        if not pull_requests:
            new_id = "1"
            pull_request_number = 1
        else:
            new_id = str(max(int(k) for k in pull_requests.keys()) + 1)
            repo_pr_numbers = [
                int(pr.get("pull_request_number", 0))
                for pr in pull_requests.values()
                if str(pr.get("repository_id")) == repository_id
            ]
            pull_request_number = max(repo_pr_numbers, default=0) + 1

        new_pr = {
            "pull_request_id": new_id,
            "repository_id": repository_id,
            "pull_request_number": int(pull_request_number),
            "title": str(title),
            "description": str(description) if description else None,
            "source_branch_name": str(source_branch_name),
            "target_branch_name": str(target_branch_name),
            "author_id": str(author_id),
            "status": str(status),
            "linked_ticket_id": str(linked_ticket_id) if linked_ticket_id else None,
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

        pull_requests[new_id] = new_pr

        return json.dumps({
            "success": True,
            "pull_request": {
                "pull_request_id": str(new_pr["pull_request_id"]),
                "repository_id": str(new_pr["repository_id"]),
                "pull_request_number": int(new_pr["pull_request_number"]),
                "title": str(new_pr["title"]),
                "description": new_pr["description"],
                "source_branch_name": str(new_pr["source_branch_name"]),
                "target_branch_name": str(new_pr["target_branch_name"]),
                "author_id": str(new_pr["author_id"]),
                "status": str(new_pr["status"]),
                "linked_ticket_id": new_pr["linked_ticket_id"],
                "merged_by": None,
                "merged_at": None,
                "closed_at": None,
                "created_at": str(new_pr["created_at"]),
                "updated_at": str(new_pr["updated_at"]),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "open_pull_request",
                "description": "Opens a new pull request in a repository for code review and merging. This tool should be used when you want to create a pull request to merge changes from a source branch into a target branch.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_name": {
                            "type": "string",
                            "description": "The name of the repository to create the pull request in",
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the pull request",
                        },
                        "source_branch_name": {
                            "type": "string",
                            "description": "The source branch containing the changes",
                        },
                        "author_id": {
                            "type": "string",
                            "description": "The ID of the user creating the pull request",
                        },
                        "target_branch_name": {
                            "type": "string",
                            "description": "The target branch to merge into. Defaults to 'main'",
                        },
                        "description": {
                            "type": "string",
                            "description": "The description of the pull request",
                        },
                        "status": {
                            "type": "string",
                            "description": "The initial status of the pull request. Defaults to 'open'",
                            "enum": ["draft", "open"],
                        },
                        "linked_ticket_id": {
                            "type": "string",
                            "description": "The ticket ID to link to this pull request",
                        },
                    },
                    "required": [
                        "repository_name",
                        "title",
                        "source_branch_name",
                        "author_id",
                    ],
                },
            },
        }
