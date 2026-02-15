import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ModifyPullRequest(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        new_status: str,
        pull_request_number: Optional[int] = None,
        pull_request_id: Optional[str] = None,
    ) -> str:
        pull_requests = data.get("pull_requests", {})
        timestamp = "2026-02-02 23:59:00"

        if not new_status:
            return json.dumps({"error": "new_status is required"})

        valid_statuses = ("open", "closed", "draft")
        if new_status not in valid_statuses:
            return json.dumps(
                {"error": f"Invalid status '{new_status}'. Must be one of: {', '.join(valid_statuses)}"}
            )

        if pull_request_number is None and pull_request_id is None:
            return json.dumps(
                {"error": "Either pull_request_number or pull_request_id must be provided"}
            )

        def build_pr_response(pr):
            return {
                "pull_request_id": str(pr["pull_request_id"]),
                "repository_id": str(pr["repository_id"]),
                "pull_request_number": int(pr["pull_request_number"]),
                "title": str(pr["title"]),
                "description": str(pr["description"]) if pr.get("description") else None,
                "source_branch_name": str(pr["source_branch_name"]),
                "target_branch_name": str(pr["target_branch_name"]),
                "author_id": str(pr["author_id"]),
                "status": str(pr["status"]),
                "linked_ticket_id": str(pr["linked_ticket_id"]) if pr.get("linked_ticket_id") else None,
                "merged_by": str(pr["merged_by"]) if pr.get("merged_by") else None,
                "merged_at": str(pr["merged_at"]) if pr.get("merged_at") else None,
                "closed_at": str(pr["closed_at"]) if pr.get("closed_at") else None,
                "created_at": str(pr["created_at"]),
                "updated_at": str(pr["updated_at"]),
            }

        pr = None

        if pull_request_number is not None and pull_request_id is not None:
            pr = pull_requests.get(str(pull_request_id))
            if not pr:
                return json.dumps(
                    {"error": f"Pull request with ID '{pull_request_id}' not found"}
                )
            if pr.get("pull_request_number") != int(pull_request_number):
                return json.dumps(
                    {"error": f"Mismatch: pull_request_id '{pull_request_id}' does not correspond to pull_request_number {int(pull_request_number)}"}
                )

        elif pull_request_id is not None:
            pr = pull_requests.get(str(pull_request_id))
            if not pr:
                return json.dumps(
                    {"error": f"Pull request with ID '{pull_request_id}' not found"}
                )

        else:
            pull_request_number = int(pull_request_number)
            for p in pull_requests.values():
                if p.get("pull_request_number") == pull_request_number:
                    pr = p
                    break
            if not pr:
                return json.dumps(
                    {"error": f"Pull request with number {pull_request_number} not found"}
                )

        if pr.get("merged_at") or pr.get("status") == "merged":
            return json.dumps(
                {"error": "Cannot modify status of a merged pull request"}
            )

        if new_status == "closed":
            pr["closed_at"] = timestamp

        pr["status"] = new_status
        pr["updated_at"] = timestamp

        return json.dumps({"success": True, "pull_request": build_pr_response(pr)})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "modify_pull_request",
                "description": "Modifies the status of an existing pull request, supporting transitions to open, closed, or draft. This tool should be used when there is a need to update the status of a pull request.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "new_status": {
                            "type": "string",
                            "description": "The new status for the pull request",
                            "enum": ["open", "closed", "draft"],
                        },
                        "pull_request_number": {
                            "type": "integer",
                            "description": "The number of the pull request",
                        },
                        "pull_request_id": {
                            "type": "string",
                            "description": "The unique identifier of the pull request",
                        },
                    },
                    "required": ["new_status"],
                    "oneOf": [
                        {"required": ["pull_request_number"]},
                        {"required": ["pull_request_id"]},
                    ],
                },
            },
        }
