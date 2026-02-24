import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateNewPullRequest(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        title: str,
        description: str,
        source_branch_name: str,
        target_branch_name: str,
        author_id: str,
        linked_ticket_id: Optional[str] = None,
    ) -> str:
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return json.dumps({
                    "success": bool(False),
                    "error": str("Wrong data format"),
                })
        if not isinstance(data, dict):
            return json.dumps({
                "success": bool(False),
                "error": str("Wrong data format"),
            })

        if repository_id is None or (isinstance(repository_id, str) and repository_id.strip() == ""):
            return json.dumps({
                "success": bool(False),
                "error": str("repository_id is required"),
            })
        if title is None or (isinstance(title, str) and title.strip() == ""):
            return json.dumps({
                "success": bool(False),
                "error": str("title is required"),
            })
        if description is None or (isinstance(description, str) and description.strip() == ""):
            return json.dumps({
                "success": bool(False),
                "error": str("description is required"),
            })
        if source_branch_name is None or (isinstance(source_branch_name, str) and source_branch_name.strip() == ""):
            return json.dumps({
                "success": bool(False),
                "error": str("source_branch_name is required"),
            })
        if target_branch_name is None or (isinstance(target_branch_name, str) and target_branch_name.strip() == ""):
            return json.dumps({
                "success": bool(False),
                "error": str("target_branch_name is required"),
            })
        if author_id is None or (isinstance(author_id, str) and author_id.strip() == ""):
            return json.dumps({
                "success": bool(False),
                "error": str("author_id is required"),
            })

        if str(source_branch_name).strip() == str(target_branch_name).strip():
            return json.dumps({
                "success": bool(False),
                "error": str("Source and target branches must differ"),
            })

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})
        pull_requests = data.get("pull_requests", {})
        tickets = data.get("tickets", {})
        users = data.get("users", {})

        author = users.get(str(author_id))
        if not author:
            return json.dumps({
                "success": bool(False),
                "error": str(f"Author with id '{author_id}' not found in users"),
            })
        if author.get("status") != "active":
            return json.dumps({
                "success": bool(False),
                "error": str(f"Author with id '{author_id}' must have active status. Current status: {author.get('status')}"),
            })

        if str(repository_id) not in repositories:
            return json.dumps({
                "success": bool(False),
                "error": str(f"Repository with id '{repository_id}' not found"),
            })

        source_branch = None
        for branch in branches.values():
            if (
                str(branch.get("repository_id")) == str(repository_id)
                and branch.get("branch_name") == source_branch_name
            ):
                source_branch = branch
                break

        if not source_branch:
            return json.dumps({
                "success": bool(False),
                "error": str(f"Source branch '{source_branch_name}' not found in repository '{repository_id}'"),
            })

        if source_branch.get("status") != "active":
            return json.dumps({
                "success": bool(False),
                "error": str(f"Source branch '{source_branch_name}' is not active. Current status: {source_branch.get('status')}"),
            })

        target_branch = None
        for branch in branches.values():
            if (
                str(branch.get("repository_id")) == str(repository_id)
                and branch.get("branch_name") == target_branch_name
            ):
                target_branch = branch
                break

        if not target_branch:
            return json.dumps({
                "success": bool(False),
                "error": str(f"Target branch '{target_branch_name}' not found in repository '{repository_id}'"),
            })

        if linked_ticket_id is not None and str(linked_ticket_id).strip() != "":
            if str(linked_ticket_id) not in tickets:
                return json.dumps({
                    "success": bool(False),
                    "error": str(f"Ticket with id '{linked_ticket_id}' not found"),
                })

            ticket = tickets[str(linked_ticket_id)]
            valid_ticket_statuses = ["open", "pending", "in_progress"]
            if ticket.get("status") not in valid_ticket_statuses:
                return json.dumps({
                    "success": bool(False),
                    "error": str(f"Ticket '{linked_ticket_id}' is not in valid state. Must be one of: {', '.join(valid_ticket_statuses)}. Current status: {ticket.get('status')}"),
                })

        if pull_requests:
            max_id = max(int(k) for k in pull_requests.keys())
            new_pr_id = str(max_id + 1)
        else:
            new_pr_id = "1"

        repo_pr_numbers = []
        for pr in pull_requests.values():
            if str(pr.get("repository_id")) != str(repository_id):
                continue
            raw = pr.get("pull_request_number", 0)
            try:
                repo_pr_numbers.append(int(raw) if raw is not None else 0)
            except (TypeError, ValueError):
                repo_pr_numbers.append(0)
        new_pr_number = int(max(repo_pr_numbers, default=0) + 1)

        static_timestamp = "2026-02-02 23:59:00"

        new_pull_request = {
            "pull_request_id": str(new_pr_id),
            "repository_id": str(repository_id),
            "pull_request_number": int(new_pr_number),
            "title": str(title),
            "description": str(description),
            "source_branch_name": str(source_branch_name),
            "target_branch_name": str(target_branch_name),
            "author_id": str(author_id),
            "status": str("open"),
            "linked_ticket_id": str(linked_ticket_id) if linked_ticket_id is not None and str(linked_ticket_id).strip() != "" else None,
            "created_at": str(static_timestamp),
            "updated_at": str(static_timestamp),
        }

        pull_requests[new_pr_id] = new_pull_request

        out_pull_request = {
            "pull_request_id": str(new_pull_request["pull_request_id"]),
            "repository_id": str(new_pull_request["repository_id"]),
            "pull_request_number": int(new_pull_request["pull_request_number"]),
            "title": str(new_pull_request["title"]),
            "description": str(new_pull_request["description"]),
            "source_branch_name": str(new_pull_request["source_branch_name"]),
            "target_branch_name": str(new_pull_request["target_branch_name"]),
            "author_id": str(new_pull_request["author_id"]),
            "status": str(new_pull_request["status"]),
            "linked_ticket_id": str(new_pull_request["linked_ticket_id"]) if new_pull_request["linked_ticket_id"] is not None else None,
            "created_at": str(new_pull_request["created_at"]),
            "updated_at": str(new_pull_request["updated_at"]),
        }
        return json.dumps({"success": bool(True), "pull_request": out_pull_request})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_new_pull_request",
                "description": "Creates a new pull request from a source branch to a target branch.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "Repository identifier where the pull request will be created.",
                        },
                        "title": {
                            "type": "string",
                            "description": "Pull request title.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Pull request description.",
                        },
                        "source_branch_name": {
                            "type": "string",
                            "description": "Source branch name.",
                        },
                        "target_branch_name": {
                            "type": "string",
                            "description": "Target branch name.",
                        },
                        "author_id": {
                            "type": "string",
                            "description": "Author user identifier; must exist in users and have active status.",
                        },
                        "linked_ticket_id": {
                            "type": "string",
                            "description": "Linked ticket identifier. Default: none.",
                        },
                    },
                    "required": [
                        "repository_id",
                        "title",
                        "description",
                        "source_branch_name",
                        "target_branch_name",
                        "author_id",
                    ],
                },
            },
        }
