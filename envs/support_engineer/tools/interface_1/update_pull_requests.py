import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdatePullRequests(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        pr_id: str,
        user_id: str,
        is_emergency_fix: Optional[bool] = None,
        execute_merge: Optional[bool] = False,
        approved_by_tech_lead_id: Optional[str] = None,
        target_branch: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not pr_id:
            return json.dumps({"success": False, "error": "Missing Argument: 'pr_id' is required."})

        if not user_id:
            return json.dumps({"success": False, "error": "Missing Argument: 'user_id' is required."})

        pull_requests = data.get("pull_requests", {})
        if not isinstance(pull_requests, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'pull_requests' must be a dictionary"})

        pr_id_str = str(pr_id).strip()
        target_pr = None

        for _, v in pull_requests.items():
            if isinstance(v, dict) and str(v.get("pull_request_id", "")).strip() == pr_id_str:
                target_pr = v
                break

        if not target_pr:
            return json.dumps({"success": False, "error": f"Not Found Error: pull_request_id '{pr_id_str}' not found."})

        timestamp = "2026-02-02 23:59:00"
        is_change_detected = False

        if is_emergency_fix is not None:
            if not isinstance(is_emergency_fix, bool):
                val_str = str(is_emergency_fix).strip().lower()
                if val_str in ['true', '1']:
                    is_emergency_fix = True
                elif val_str in ['false', '0']:
                    is_emergency_fix = False
                else:
                    return json.dumps({"success": False, "error": "Invalid Argument: 'is_emergency_fix' must be a boolean."})

            if target_pr.get("is_emergency_fix") != is_emergency_fix:
                target_pr["is_emergency_fix"] = is_emergency_fix
                is_change_detected = True

        if target_branch is not None:
            target_branch_str = str(target_branch).strip()
            if target_pr.get("target_branch_name") != target_branch_str:
                target_pr["target_branch_name"] = target_branch_str
                is_change_detected = True

        if approved_by_tech_lead_id is not None:
            tech_lead_str = str(approved_by_tech_lead_id).strip()
            if target_pr.get("assigned_team_lead") != tech_lead_str:
                target_pr["assigned_team_lead"] = tech_lead_str
                is_change_detected = True

        execute_merge_bool = False
        if execute_merge is not None:
            if not isinstance(execute_merge, bool):
                val_str = str(execute_merge).strip().lower()
                if val_str in ['true', '1']:
                    execute_merge_bool = True
            else:
                execute_merge_bool = execute_merge

        if execute_merge_bool:
            current_status = str(target_pr.get("status", "")).lower()
            if current_status != "open":
                return json.dumps({"success": False, "error": f"Conflict Error: PR is '{current_status}' and cannot be merged. Must be 'open'."})

            coverage_ok = bool(target_pr.get("gate_test_coverage", False))
            is_emergency = bool(target_pr.get("is_emergency_fix", False))
            assigned_lead = target_pr.get("assigned_team_lead")

            if not coverage_ok:
                if not is_emergency:
                    return json.dumps({"success": False, "error": "Policy Violation: Coverage Gate failed. Set 'is_emergency_fix' to true to bypass."})
                if not assigned_lead:
                    return json.dumps({"success": False, "error": "Policy Violation: Coverage Gate failed. Emergency bypass requires 'approved_by_tech_lead_id'."})

            target_pr["status"] = "merged"
            target_pr["merged_by"] = str(user_id).strip()
            target_pr["merged_at"] = timestamp
            target_pr["closed_at"] = timestamp
            is_change_detected = True

        if is_change_detected:
            target_pr["updated_at"] = timestamp
            action_msg = "merged" if execute_merge_bool else "updated"
            return json.dumps({
                "success": True,
                "pull_request": target_pr,
                "message": f"Pull Request '{pr_id_str}' {action_msg} successfully."
            })
        else:
            return json.dumps({
                "success": False,
                "error": "No update Detected",
                "message": f"No-Op: Pull Request '{pr_id_str}' already has the provided values and merge was not executed."
            })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_pull_requests",
                "description": (
                    " Updates an existing Pull Request's metadata and executes code merges. Specifically designed to handle emergency deployments and hotfixes.\n"
                    " Purpose: Facilitates the 'Deploy Emergency Hotfixes' SOP. It allows a Support Engineer to update PR metadata, flag a PR as an emergency, record Tech Lead approval, and bypass standard testing constraints (Coverage Gate) to execute a merge directly to the production branch to restore service.\n"
                    " When to use: Use this tool when handling a Critical (P0) ticket that requires an immediate hotfix. Apply it to mark a PR's 'is_emergency_fix' status to 'true', designate the target branch as 'production', set the 'approved_by_tech_lead_id', and set 'execute_merge' to 'true' to deploy.\n"
                    " Returns: Returns a JSON string containing a success boolean, the updated pull request dictionary object reflecting its new emergency and merge status, and a success message. Fails if a merge is attempted with a failing coverage gate but without the emergency flag and Tech Lead approval."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pr_id": {
                            "type": "string",
                            "description": "The unique identifier of the Pull Request to update or merge."
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The unique user identifier of the person executing the update or merge."
                        },
                        "is_emergency_fix": {
                            "type": "boolean",
                            "description": "Flag to mark the PR as an emergency fix. Set to true to bypass the Coverage Gate."
                        },
                        "execute_merge": {
                            "type": "boolean",
                            "description": "Set to true to execute the merge operation. If false, only metadata will be updated."
                        },
                        "approved_by_tech_lead_id": {
                            "type": "string",
                            "description": "The user identifier of the Tech Lead who approved bypassing the normal protocols. Required if executing an emergency merge with a failing Coverage Gate."
                        },
                        "target_branch": {
                            "type": "string",
                            "description": "The branch to merge the PR into (e.g., 'production'). Overrides the original target branch of the ticket."
                        }
                    },
                    "required": ["pr_id", "user_id"]
                }
            }
        }
