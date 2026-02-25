import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class AddItemUpdate(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        work_item_id: str,
        updated_by: str,
        status: str,
        reason: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format for work_item_updates"}
            )

        if work_item_id is None:
            return json.dumps({"success": False, "error": "work_item_id is required"})

        if updated_by is None:
            return json.dumps({"success": False, "error": "updated_by is required"})

        if not status:
            return json.dumps({"success": False, "error": "status is required"})

        valid_statuses = [
            "open",
            "in_progress",
            "done",
            "closed",
            "blocked",
            "rejected",
            "pending_review",
            "approved",
            "backlog",
        ]
        if status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}",
                }
            )

        if reason is not None and len(reason) > 500:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Reason exceeds maximum length of 500 characters (current length: {len(reason)})",
                }
            )

        work_items = data.get("work_items", {})
        work_item = None

        for _work_item_key, work_item_data in work_items.items():
            if str(work_item_data.get("work_item_id")) == str(work_item_id):
                work_item = work_item_data
                break

        if not work_item:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Work item with ID {work_item_id} not found",
                }
            )

        old_status = work_item.get("status", "backlog")

        if old_status == status:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Work item status is already '{status}'. No update needed.",
                }
            )

        users = data.get("users", {})
        user_exists = False

        for _user_key, user_data in users.items():
            if str(user_data.get("user_id")) == str(updated_by):
                user_exists = True
                break

        if not user_exists:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with ID {updated_by} not found in users table",
                }
            )

        fields_data = {
            "old_status": old_status,
            "new_status": status,
            "changed_fields": ["status"],
        }
        fields_json = json.dumps(fields_data)

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        work_item_updates = data.setdefault("work_item_updates", {})
        update_id = generate_id(work_item_updates)
        timestamp = "2026-02-11T23:59:00"

        new_update = {
            "update_id": str(update_id),
            "work_item_id": str(work_item_id),
            "updated_by": str(updated_by),
            "fields_json": str(fields_json),
            "reason": str(reason) if reason is not None else None,
            "created_at": str(timestamp),
        }

        work_item_updates[str(update_id)] = new_update
        work_item["status"] = status

        return json.dumps(
            {
                "success": True,
                "update": new_update,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_item_update",
                "description": "Add an update record for a work item status change. Use this to track status transitions and create an audit trail of work item updates.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "work_item_id": {
                            "type": "string",
                            "description": "The work item ID to add an update for",
                        },
                        "updated_by": {
                            "type": "string",
                            "description": "The user ID of the person making the update",
                        },
                        "status": {
                            "type": "string",
                            "description": "The new status for the work item",
                            "enum": [
                                "open",
                                "in_progress",
                                "done",
                                "closed",
                                "blocked",
                                "rejected",
                                "pending_review",
                                "approved",
                                "backlog",
                            ],
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for the update",
                        },
                    },
                    "required": ["work_item_id", "updated_by", "status"],
                },
            },
        }
