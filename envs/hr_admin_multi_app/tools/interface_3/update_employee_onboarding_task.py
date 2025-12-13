import json
from typing import Any, Dict

from tau_bench.envs.tool import Tool


class UpdateEmployeeOnboardingTask(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        task_id: str,
        new_manager_id: str,
    ) -> str:
        """
        Update/reassign an onboarding task to a different manager.
        
        Args:
            data: The database dictionary containing all tables.
            task_id: The ID of the onboarding task to update (required).
            new_manager_id: The ID of the new manager to assign the task to (required).
        
        Returns:
            JSON string with the updated task record.
        """
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not task_id:
            return json.dumps({"error": "Missing required parameter: task_id is required"})
        if not new_manager_id:
            return json.dumps({"error": "Missing required parameter: new_manager_id is required"})

        task_id = str(task_id)
        new_manager_id = str(new_manager_id)

        checklist_tasks = data.get("checklist_tasks", {})
        employees = data.get("employees", {})

        if task_id not in checklist_tasks:
            return json.dumps({"error": f"Onboarding task with ID '{task_id}' not found"})

        if new_manager_id not in employees:
            return json.dumps({"error": f"Manager with ID '{new_manager_id}' not found"})

        task = checklist_tasks[task_id]
        task["assigned_manager_id"] = new_manager_id
        task["last_updated"] = "2025-11-16T23:59:00"

        return json.dumps(task)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_employee_onboarding_task",
                "description": (
                    "Updates/reassigns an onboarding task to a different manager. "
                    "Use this when responsibility for a task needs to be transferred."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "The ID of the onboarding task to update (required).",
                        },
                        "new_manager_id": {
                            "type": "string",
                            "description": "The ID of the new manager to assign the task to (required).",
                        },
                    },
                    "required": ["task_id", "new_manager_id"],
                },
            },
        }
