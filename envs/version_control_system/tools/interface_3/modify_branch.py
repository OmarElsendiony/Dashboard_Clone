import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ModifyBranch(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        branch_id: str,
        action: str,
        commit_sha: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not branch_id:
            return json.dumps({"success": False, "error": "branch_id is required to modify branch"})

        if not action:
            return json.dumps({"success": False, "error": "action is required to modify branch"})

        # Validate action
        valid_actions = ["delete", "update"]
        if action not in valid_actions:
            return json.dumps({"success": False, "error": f"Invalid action '{action}'. Valid values: delete, update"})

        # Validate commit_sha is required for update action
        if action == "update" and not commit_sha:
            return json.dumps({"success": False, "error": "commit_sha is required when action is 'update'"})

        branches = data.get("branches", {})
        commits = data.get("commits", {})

        # Validate branch exists
        if str(branch_id) not in branches:
            return json.dumps({"success": False, "error": f"Branch with id '{branch_id}' not found"})

        branch = branches[str(branch_id)]

        if action == "delete":
            # Delete the branch
            deleted_branch = branches.pop(str(branch_id))
            return json.dumps({
                "success": True,
                "result": deleted_branch,
                "message": f"Branch '{deleted_branch.get('branch_name')}' has been deleted"
            })

        elif action == "update":
            # Validate commit_sha exists and belongs to the same repository
            branch_repo_id = branch.get("repository_id")
            commit_found = False
            for commit_id, commit in commits.items():
                if commit.get("commit_sha") == commit_sha:
                    if str(commit.get("repository_id")) != str(branch_repo_id):
                        return json.dumps({"success": False, "error": f"Commit with SHA '{commit_sha}' does not belong to the same repository as the branch"})
                    commit_found = True
                    break
            if not commit_found:
                return json.dumps({"success": False, "error": f"Commit with SHA '{commit_sha}' not found"})

            branch["commit_sha"] = commit_sha
            branch["updated_at"] = "2026-01-01T23:59:00"
            return json.dumps({
                "success": True,
                "result": branch,
                "message": f"Branch '{branch.get('branch_name')}' has been updated to commit '{commit_sha}'"
            })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "modify_branch",
                "description": "Updates or deletes a branch in a repository. Use action 'update' to update, or action 'delete' to remove the branch.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "branch_id": {
                            "type": "string",
                            "description": "The unique identifier of the branch to modify."
                        },
                        "action": {
                            "type": "string",
                            "description": "The action to perform on the branch. Valid values: delete, update."
                        },
                        "commit_sha": {
                            "type": "string",
                            "description": "The SHA hash of the commit to point the branch to. Required when action is 'update' (optional)."
                        }
                    },
                    "required": ["branch_id", "action"]
                }
            }
        }
