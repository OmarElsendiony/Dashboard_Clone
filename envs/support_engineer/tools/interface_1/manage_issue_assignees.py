import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool


class ManageIssueAssignees(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        action: str,
        issue_id: str,
        user_ids: List[str],
        role: Optional[str] = "owner",
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })

        if not action:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'action' is required."
            })

        if not issue_id:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'issue_id' is required."
            })

        if not user_ids:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'user_ids' is required."
            })

        if not isinstance(action, str) or not action.strip():
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: action must be a non-empty string."
            })

        action_norm = action.strip().lower()
        valid_actions = ["add", "remove"]

        if action_norm not in valid_actions:
            return json.dumps({
                "success": False,
                "error": f"Invalid Argument: action must be one of {valid_actions}."
            })

        if not isinstance(issue_id, str) or not issue_id.strip():
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: issue_id must be a non-empty string."
            })

        if not isinstance(user_ids, list) or len(user_ids) == 0:
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: user_ids must be a non-empty list."
            })

        normalized_user_ids = []
        seen = set()
        for raw in user_ids:
            uid = str(raw).strip()
            if not uid:
                continue
            if uid in seen:
                continue
            seen.add(uid)
            normalized_user_ids.append(uid)

        if len(normalized_user_ids) == 0:
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: user_ids must contain at least one valid user id."
            })

        if role is None:
            role = "owner"

        if not isinstance(role, str) or not role.strip():
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: role must be a non-empty string when provided."
            })

        role_norm = role.strip().lower()
        valid_roles = ["owner", "assignee"]

        if role_norm not in valid_roles:
            return json.dumps({
                "success": False,
                "error": f"Invalid Argument: role must be one of {valid_roles}."
            })

        issues = data.get("issues", {})
        users = data.get("users", {})
        issue_assignees = data.get("issue_assignees")

        if not isinstance(issues, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'issues' must be a dictionary"
            })

        if not isinstance(users, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'users' must be a dictionary"
            })

        if issue_assignees is None:
            issue_assignees = {}
            data["issue_assignees"] = issue_assignees

        if not isinstance(issue_assignees, (dict, list)):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'issue_assignees' must be a dictionary or list"
            })

        ikey = str(issue_id).strip()
        issue_obj = issues.get(ikey)

        if issue_obj is None:
            for v in issues.values():
                if isinstance(v, dict) and str(v.get("issue_id", "")).strip() == ikey:
                    issue_obj = v
                    break

        if issue_obj is None:
            return json.dumps({
                "success": False,
                "error": f"Not Found Error: issue_id '{issue_id}' not found."
            })

        for uid in normalized_user_ids:
            if uid not in users:
                return json.dumps({
                    "success": False,
                    "error": f"Authorization Error: user_id '{uid}' not found."
                })

        timestamp = "2026-02-02 23:59:00"

        existing_pairs = set()
        rows = issue_assignees.values() if isinstance(issue_assignees, dict) else issue_assignees
        for row in rows:
            if not isinstance(row, dict):
                continue
            existing_pairs.add((
                str(row.get("issue_id", "")),
                str(row.get("user_id", "")),
                str(row.get("role", "")).lower()
            ))

        added = 0
        removed = 0

        if action_norm == "add":
            if isinstance(issue_assignees, dict):
                numeric_keys = []
                for k in issue_assignees.keys():
                    try:
                        numeric_keys.append(int(str(k)))
                    except Exception:
                        continue
                next_key = (max(numeric_keys) + 1) if numeric_keys else (len(issue_assignees) + 1)

                for uid in normalized_user_ids:
                    pair = (ikey, uid, role_norm)
                    if pair in existing_pairs:
                        continue
                    issue_assignees[str(next_key)] = {
                        "issue_id": ikey,
                        "user_id": uid,
                        "role": role_norm,
                        "created_at": timestamp
                    }
                    next_key += 1
                    added += 1

            if isinstance(issue_assignees, list):
                for uid in normalized_user_ids:
                    pair = (ikey, uid, role_norm)
                    if pair in existing_pairs:
                        continue
                    issue_assignees.append({
                        "issue_id": ikey,
                        "user_id": uid,
                        "role": role_norm,
                        "created_at": timestamp
                    })
                    added += 1

            issue_obj["updated_at"] = timestamp

            return json.dumps({
                "success": True,
                "action": "add",
                "issue_id": ikey,
                "role": role_norm,
                "added_count": added,
                "message": "Issue assignees added successfully."
            })

        if isinstance(issue_assignees, dict):
            keys_to_delete = []
            for k, row in issue_assignees.items():
                if not isinstance(row, dict):
                    continue
                if str(row.get("issue_id", "")).strip() == ikey and str(row.get("role", "")).lower() == role_norm:
                    if str(row.get("user_id", "")).strip() in normalized_user_ids:
                        keys_to_delete.append(k)

            for k in keys_to_delete:
                try:
                    del issue_assignees[k]
                    removed += 1
                except Exception:
                    continue

        if isinstance(issue_assignees, list):
            new_list = []
            for row in issue_assignees:
                if not isinstance(row, dict):
                    new_list.append(row)
                    continue
                if str(row.get("issue_id", "")).strip() == ikey and str(row.get("role", "")).lower() == role_norm:
                    if str(row.get("user_id", "")).strip() in normalized_user_ids:
                        removed += 1
                        continue
                new_list.append(row)
            issue_assignees[:] = new_list

        issue_obj["updated_at"] = timestamp

        return json.dumps({
            "success": True,
            "action": "remove",
            "issue_id": ikey,
            "role": role_norm,
            "removed_count": removed,
            "message": "Issue assignees removed successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "manage_issue_assignees",
                "description": (
                    "Updates the set of users responsible for a repository issue by modifying its assignment roster."

                    "PURPOSE: Ensures clear accountability and ownership by dynamically managing the list of users tasked with investigation, remediation, and follow-up."

                    "WHEN TO USE: When assigning a technical lead to a critical bug, adding owners during an escalation, or removing assignees during shift handoffs, workload rebalancing, or incident resolution."

                    "RETURNS: The outcome of the assignment update, allowing downstream steps to reliably determine current issue ownership and accountability."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["add", "remove"],
                            "description": "Assignment roster modification action."
                        },
                        "issue_id": {
                            "type": "string",
                            "description": "Repository issue identifier whose assignees should be updated."
                        },
                        "user_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "User identifiers to add to or remove from the issue."
                        },
                        "role": {
                            "type": "string",
                            "enum": ["owner", "assignee"],
                            "description": "Assignment role applied to the users (optional )"
                        }
                    },
                    "required": ["action", "issue_id", "user_ids"]
                }
            }
        }
