import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class UpdateChecklistTask(Tool):
    """Update status or assignment for an existing checklist task."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        checklist_id: str,
        task_id: str,
        status: Optional[str] = None,
        manager_id: Optional[str] = None,
    ) -> str:
        """
        Update a checklist task belonging to a checklist. Allows changing status and/or assigned manager.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        checklist_tasks = data.get("checklist_tasks")
        checklists = data.get("checklists")
        employees = data.get("employees", {})

        if not isinstance(checklist_tasks, dict) or not isinstance(checklists, dict):
            return json.dumps({"success": False, "error": "Missing checklists or checklist_tasks store"})

        if not checklist_id or not checklist_id.strip():
            return json.dumps({"success": False, "error": "checklist_id is required"})
        if checklist_id not in checklists:
            return json.dumps({"success": False, "error": f"Checklist '{checklist_id}' not found"})

        if not task_id or not task_id.strip():
            return json.dumps({"success": False, "error": "task_id is required"})

        task = checklist_tasks.get(task_id)
        if not task or task.get("checklist_id") != checklist_id:
            return json.dumps({"success": False, "error": "Task not found for the given checklist"})

        updated = False

        if status:
            normalized_status = status.strip().lower()
            if normalized_status not in {"pending", "completed"}:
                return json.dumps({"success": False, "error": "status must be pending or completed"})
            task["status"] = normalized_status
            updated = True

        if manager_id is not None:
            if manager_id == "":
                task["assigned_manager_id"] = None
            else:
                manager = employees.get(manager_id)
                if not manager:
                    return json.dumps({"success": False, "error": f"Manager '{manager_id}' not found"})
                if str(manager.get("status", "")).strip().lower() != "active":
                    return json.dumps({"success": False, "error": f"Manager '{manager_id}' is not active"})
                task["assigned_manager_id"] = manager_id
            updated = True

        if not updated:
            return json.dumps({"success": False, "error": "No updates provided"})

        task["last_updated"] = "2025-12-12T12:00:00"

        return json.dumps(
            {
                "success": True,
                "message": f"Task '{task_id}' updated",
                "task": task,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_checklist_task",
                "description": "Update the status or manager assignment of a checklist task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "checklist_id": {
                            "type": "string",
                            "description": "Identifier of the checklist that owns the task.",
                        },
                        "task_id": {
                            "type": "string",
                            "description": "Identifier of the task to update.",
                        },
                        "status": {
                            "type": "string",
                            "description": "New task status; allowed values are pending or completed.",
                        },
                        "manager_id": {
                            "type": "string",
                            "description": "New manager assignment; must reference an active employee. Send empty string to clear.",
                        },
                    },
                    "required": ["checklist_id", "task_id"],
                },
            },
        }
