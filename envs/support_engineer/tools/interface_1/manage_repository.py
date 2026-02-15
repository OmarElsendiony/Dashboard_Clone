import json
import uuid
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class ManageRepository(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        action: str,
        user_id: str,
        repository_id: str,
        branch_name: str,
        source_branch: str = "main",
        file_name: Optional[str] = None,
        content: Optional[str] = None,
        commit_message: Optional[str] = None,
        ticket_id: Optional[str] = None,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not action:
            return json.dumps({"success": False, "error": "Missing Argument: 'action' is required."})

        if not user_id:
            return json.dumps({"success": False, "error": "Missing Argument: 'user_id' is required."})

        if not repository_id:
            return json.dumps({"success": False, "error": "Missing Argument: 'repository_id' is required."})

        if not branch_name:
            return json.dumps({"success": False, "error": "Missing Argument: 'branch_name' is required."})

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})
        files_db = data.get("files", {})
        commits_db = data.get("commits", {})

        valid_actions = ["create_branch", "commit_file"]
        if action not in valid_actions:
            return json.dumps({
                "success": False,
                "error": f"Invalid Argument: action must be one of {valid_actions}."
            })

        timestamp = "2026-02-02T23:59:00"

        if action == "create_branch":
            if repository_id not in repositories:
                return json.dumps({"success": False, "error": f"Repository '{repository_id}' not found."})

            for b in branches.values():
                if str(b.get("repository_id")) == str(repository_id) and b.get("branch_name") == branch_name:
                    return json.dumps({"success": False, "error": f"Branch '{branch_name}' already exists in repo '{repository_id}'."})

            valid_prefixes = ["fix/", "feat/", "hotfix/", "chore/"]
            if not any(branch_name.startswith(p) for p in valid_prefixes):
                return json.dumps({
                    "success": False,
                    "error": f"Policy Violation: Branch name '{branch_name}' must start with 'fix/', 'feat/', 'hotfix/', or 'chore/'."
                })

            new_id = str(len(branches) + 1)

            new_branch = {
                "branch_id": new_id,
                "repository_id": repository_id,
                "branch_name": branch_name,
                "base_branch": source_branch,
                "ticket_id": ticket_id,
                "creator_id": user_id,
                "status": "active",
                "created_at": timestamp,
                "updated_at": timestamp
            }
            branches[new_id] = new_branch

            return json.dumps({
                "success": True,
                "branch": new_branch,
                "ticket_id": ticket_id,
                "message": f"Branch '{branch_name}' created successfully linked to ticket {ticket_id}."
            })

        if action == "commit_file":
            if not file_name:
                return json.dumps({"success": False, "error": "Missing Argument: 'file_name' is required for commit_file."})
            if content is None:
                return json.dumps({"success": False, "error": "Missing Argument: 'content' is required for commit_file."})
            if not ticket_id:
                return json.dumps({"success": False, "error": "Missing Argument: 'ticket_id' is required for audit traceability."})

            branch_id = None
            for b in branches.values():
                if str(b.get("repository_id")) == str(repository_id) and b.get("branch_name") == branch_name:
                    branch_id = b.get("branch_id")
                    break

            if not branch_id:
                return json.dumps({"success": False, "error": f"Branch '{branch_name}' not found in repo '{repository_id}'."})

            new_commit_id = str(len(commits_db) + 1)
            new_commit = {
                "commit_id": new_commit_id,
                "repository_id": repository_id,
                "branch_id": branch_id,
                "commit_sha": f"{uuid.uuid4().hex[:7]}",
                "author_id": user_id,
                "commit_message": commit_message or f"Update {file_name}",
                "ticket_id": ticket_id,
                "created_at": timestamp
            }
            commits_db[new_commit_id] = new_commit

            target_file_key = None
            for k, f in files_db.items():
                if str(f.get("branch_id")) == str(branch_id) and (f.get("file_name") == file_name or f.get("file_path") == file_name):
                    target_file_key = k
                    break

            if target_file_key:
                files_db[target_file_key]["content"] = content
                files_db[target_file_key]["last_commit_id"] = new_commit_id
                files_db[target_file_key]["updated_at"] = timestamp
                op_type = "updated"
            else:
                new_file_id = str(len(files_db) + 1)
                files_db[new_file_id] = {
                    "file_id": new_file_id,
                    "repository_id": repository_id,
                    "branch_id": branch_id,
                    "file_path": file_name,
                    "file_name": file_name,
                    "content": content,
                    "last_commit_id": new_commit_id,
                    "created_at": timestamp,
                    "updated_at": timestamp
                }
                op_type = "created"

            return json.dumps({
                "success": True,
                "file": file_name,
                "branch": branch_name,
                "commit_sha": new_commit["commit_sha"],
                "ticket_id": ticket_id,
                "message": f"File '{file_name}' {op_type} on branch '{branch_name}' (Ticket: {ticket_id})."
            })

        return json.dumps({"success": False, "error": "Unknown action."})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "manage_repository",
                "description": (
                    "Handles core Git operations for code management. "
                    "PRIMARY ACTIONS:\n"
                    "1. 'create_branch': Initializes a new branch. Enforces strict naming (fix/, feat/, etc.) and schema consistency with StartBranch.\n"
                    "2. 'commit_file': Pushes a single file's content to a branch. Requires 'ticket_id' for audit compliance.\n"
                    "Use this tool to prepare code BEFORE creating a Pull Request."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["create_branch", "commit_file"],
                            "description": "REQUIRED. The Git operation to perform."
                        },
                        "user_id": {
                            "type": "string",
                            "description": "REQUIRED. The ID of the user performing the action."
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "REQUIRED. The target repository identifier."
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "REQUIRED. The name of the branch. Must follow 'type/...' format."
                        },
                        "source_branch": {
                            "type": "string",
                            "description": "OPTIONAL. The starting point for 'create_branch'. Defaults to 'main'."
                        },
                        "file_name": {
                            "type": "string",
                            "description": "CONDITIONAL. Required for 'commit_file'. The path/name of the file."
                        },
                        "content": {
                            "type": "string",
                            "description": "CONDITIONAL. Required for 'commit_file'. The full text content of the file."
                        },
                        "commit_message": {
                            "type": "string",
                            "description": "OPTIONAL. A description of the changes for 'commit_file'."
                        },
                        "ticket_id": {
                            "type": "string",
                            "description": "CONDITIONAL. Required for 'commit_file' (audit linking)."
                        }
                    },
                    "required": ["action", "user_id", "repository_id", "branch_name"]
                }
            }
        }
