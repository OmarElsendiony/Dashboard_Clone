import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdateWorkItem(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        work_item_id: str,
        status: Optional[str] = None,
        assignee_user_id: Optional[str] = None,
    ) -> str:
        timestamp = "2026-02-11T23:59:00"

        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        if not work_item_id or not str(work_item_id).strip():
            return json.dumps(
                {
                    "success": False,
                    "error": "Missing required parameter: 'work_item_id'",
                }
            )

        if status is None and assignee_user_id is None:
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        "At least one of 'status' or 'assignee_user_id' must be provided"
                    ),
                }
            )

        work_item_id_str = str(work_item_id).strip()
        status_str = str(status).strip().lower() if status is not None else None
        assignee_user_id_str = (
            str(assignee_user_id).strip() if assignee_user_id is not None else None
        )

        valid_statuses = ["backlog", "in_progress", "blocked", "pending_review", "done"]
        if status_str is not None and status_str not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Invalid status '{status_str}'. "
                        f"Must be one of: {', '.join(valid_statuses)}"
                    ),
                }
            )

        work_items_dict = data.get("work_items", {})
        users_dict = data.get("users", {})

        if work_item_id_str not in work_items_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Work item with ID '{work_item_id_str}' not found",
                }
            )

        work_item = work_items_dict[work_item_id_str]

        if not isinstance(work_item, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Invalid work item data structure for ID '{work_item_id_str}'"
                    ),
                }
            )

        current_status = str(work_item.get("status", "")).strip().lower()
        if current_status == "closed":
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Work item '{work_item_id_str}' is closed and cannot be updated"
                    ),
                }
            )

        if assignee_user_id_str is not None:
            if assignee_user_id_str not in users_dict:
                return json.dumps(
                    {
                        "success": False,
                        "error": (
                            f"Assignee user with ID '{assignee_user_id_str}' not found"
                        ),
                    }
                )

            assignee = users_dict[assignee_user_id_str]
            if not isinstance(assignee, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": (
                            f"Invalid user data structure for assignee ID "
                            f"'{assignee_user_id_str}'"
                        ),
                    }
                )

            assignee_status = str(assignee.get("status", "")).strip().lower()
            if assignee_status != "active":
                return json.dumps(
                    {
                        "success": False,
                        "error": (
                            f"Assignee user '{assignee_user_id_str}' is not active "
                            f"(status: '{assignee_status}')"
                        ),
                    }
                )

        if status_str is not None:
            work_item["status"] = status_str

        if assignee_user_id_str is not None:
            work_item["assignee_user_id"] = assignee_user_id_str

        work_item["updated_at"] = timestamp

        work_items_dict[work_item_id_str] = work_item

        return json.dumps(
            {
                "success": True,
                "work_item": work_item,
                "message": (f"Work item '{work_item_id_str}' updated successfully"),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_work_item",
                "description": "Updates the status or assignee of an existing work item. "
                    "Exactly one or both of 'status' and 'assignee_user_id' must be supplied "
                    "Used when assigning an owner to an unassigned task, progressing task status during execution, "
                    "reverting incorrectly completed tasks, blocking tasks tied to active incidents "
                    "and resuming blocked tasks after incident resolution Closed work items cannot be updated.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "work_item_id": {
                            "type": "string",
                            "description": "The unique identifier of the work item to update. ",
                        },
                        "status": {
                            "type": "string",
                            "description": "The new status to set on the work item. ",
                            "enum": [
                                "backlog",
                                "in_progress",
                                "blocked",
                                "pending_review",
                                "done",
                            ],
                        },
                        "assignee_user_id": {
                            "type": "string",
                            "description": "The unique identifier of the user to assign the work item to. ",
                        },
                    },
                    "required": ["work_item_id"],
                    "anyOf": [
                        {"required": ["status"]},
                        {"required": ["assignee_user_id"]},
                    ],
                },
            },
        }
