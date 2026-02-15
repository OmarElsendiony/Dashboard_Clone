import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class ManagePullRequests(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        action: str,
        user_id: str,
        repository_id: Optional[str] = None,
        source_branch: Optional[str] = None,
        target_branch: Optional[str] = "main",
        title: Optional[str] = None,
        description: Optional[str] = None,
        ticket_id: Optional[str] = None,
        pr_id: Optional[str] = None,
        emergency: bool = False,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not action:
            return json.dumps({"success": False, "error": "Missing Argument: 'action' is required."})

        if not user_id:
            return json.dumps({"success": False, "error": "Missing Argument: 'user_id' is required."})

        branches = data.get("branches", {})
        pull_requests = data.get("pull_requests", {})
        files_db = data.get("files", {})

        valid_actions = ["create_pr", "merge_pr"]
        if action not in valid_actions:
            return json.dumps({
                "success": False,
                "error": f"Invalid Argument: action must be one of {valid_actions}."
            })

        timestamp = "2026-02-02T23:59:00"

        if action == "create_pr":
            if not repository_id:
                return json.dumps({"success": False, "error": "Missing Argument: 'repository_id' is required for create_pr."})
            if not source_branch:
                return json.dumps({"success": False, "error": "Missing Argument: 'source_branch' is required for create_pr."})
            if not title:
                return json.dumps({"success": False, "error": "Missing Argument: 'title' is required for create_pr."})
            if not ticket_id:
                return json.dumps({"success": False, "error": "Missing Argument: 'ticket_id' is required for create_pr."})

            branch_id = None
            for b in branches.values():
                if str(b.get("repository_id")) == str(repository_id) and b.get("branch_name") == source_branch:
                    branch_id = b.get("branch_id")
                    break

            detected_files = []
            if branch_id:
                for f in files_db.values():
                    if str(f.get("branch_id")) == str(branch_id):
                        detected_files.append(f.get("file_name"))

            gate_traceability = f"Closes {ticket_id}" in (description or "")
            gate_coverage = any("test" in f.lower() or "spec" in f.lower() for f in detected_files)

            new_id = str(len(pull_requests) + 1)

            new_pr = {
                "pull_request_id": new_id,
                "repository_id": repository_id,
                "title": title,
                "description": description,
                "source_branch_name": source_branch,
                "target_branch_name": target_branch,
                "author_id": user_id,
                "status": "open",
                "linked_ticket_id": ticket_id,
                "files": detected_files,
                "file_count": len(detected_files),
                "gate_traceability": gate_traceability,
                "gate_test_coverage": gate_coverage,
                "is_emergency": False,
                "created_at": timestamp,
                "updated_at": timestamp
            }
            pull_requests[new_id] = new_pr

            msg = f"PR #{new_id} created with {len(detected_files)} files."
            if not gate_traceability:
                msg += " WARNING: Traceability Gate Failed (Description missing 'Closes [TicketID]')."
            if not gate_coverage:
                msg += " WARNING: Coverage Gate Failed (No test files detected)."

            return json.dumps({
                "success": True,
                "pull_request": new_pr,
                "message": msg
            })

        if action == "merge_pr":
            if not pr_id:
                return json.dumps({"success": False, "error": "Missing Argument: 'pr_id' is required for merge_pr."})

            target_pr = pull_requests.get(str(pr_id))
            if not target_pr:
                return json.dumps({"success": False, "error": f"PR ID '{pr_id}' not found."})

            if target_pr["status"] != "open":
                return json.dumps({"success": False, "error": f"PR is {target_pr['status']} and cannot be merged."})

            if not target_pr["gate_test_coverage"] and not emergency:
                return json.dumps({
                    "success": False,
                    "error": "Policy Violation: Coverage Gate failed. Use 'emergency=True' to bypass if authorized."
                })

            if emergency:
                target_pr["is_emergency"] = True

            target_pr["status"] = "merged"
            target_pr["merged_by"] = user_id
            target_pr["updated_at"] = timestamp

            return json.dumps({
                "success": True,
                "pull_request": target_pr,
                "message": f"PR #{pr_id} merged successfully."
            })

        return json.dumps({"success": False, "error": "Unknown action."})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "manage_pull_requests",
                "description": (
                    "Manages the review and merging of code changes via Pull Requests. "
                    "PRIMARY ACTIONS:\n"
                    "1. 'create_pr': Submits code for review. Automatically detects all files committed to the source branch and runs validation gates (Traceability & Test Coverage).\n"
                    "2. 'merge_pr': Merges an open PR into the target branch. Enforces quality gates unless the 'emergency' flag is used.\n"
                    "Use this tool AFTER preparing your code with 'manage_repository'."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["create_pr", "merge_pr"],
                            "description": "REQUIRED. The PR operation to perform."
                        },
                        "user_id": {
                            "type": "string",
                            "description": "REQUIRED. The ID of the user performing the action."
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "CONDITIONAL. Required for 'create_pr' to identify the project."
                        },
                        "source_branch": {
                            "type": "string",
                            "description": "CONDITIONAL. Required for 'create_pr'. The branch containing your changes."
                        },
                        "target_branch": {
                            "type": "string",
                            "description": "OPTIONAL. The branch to merge into. Defaults to 'main'."
                        },
                        "title": {
                            "type": "string",
                            "description": "CONDITIONAL. Required for 'create_pr'. A short summary of the changes."
                        },
                        "description": {
                            "type": "string",
                            "description": "CONDITIONAL. Required for 'create_pr'. Must contain 'Closes [TicketID]' to pass the Traceability Gate."
                        },
                        "ticket_id": {
                            "type": "string",
                            "description": "CONDITIONAL. Required for 'create_pr' for linking purposes."
                        },
                        "pr_id": {
                            "type": "string",
                            "description": "CONDITIONAL. Required for 'merge_pr'. The unique ID of the PR to merge."
                        },
                        "emergency": {
                            "type": "boolean",
                            "description": "OPTIONAL. Set to True to bypass the Test Coverage Gate during 'merge_pr' for critical hotfixes."
                        }
                    },
                    "required": ["action", "user_id"]
                }
            }
        }
