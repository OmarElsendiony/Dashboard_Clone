import json
from typing import Any, Dict, List, Optional

from tau_bench.envs.tool import Tool


class UpdateOnboardingPacket(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        checklist_id: str,
        updates: Optional[Dict[str, Any]] = None,
        task_updates: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Update an existing onboarding packet/checklist and its tasks.
        
        Args:
            data: The database dictionary containing all tables.
            checklist_id: The ID of the onboarding checklist to update (required).
            updates: Optional JSON object containing checklist fields to update.
                Supported fields: status.
                status allowed values: 'pending', 'completed'.
            task_updates: Optional list of task update objects. Each object should have:
                task_id (required): The ID of the task to update.
                status (optional): Task status. Allowed values: 'pending', 'completed'.
                due_date (optional): New due date in format (YYYY-MM-DD).
                assigned_manager_id (optional): New manager ID for the task.
        
        Returns:
            JSON string with the updated onboarding checklist and tasks.
        """
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not checklist_id:
            return json.dumps({"error": "Missing required parameter: checklist_id is required"})

        checklist_id = str(checklist_id)
        checklists = data.get("checklists", {})
        checklist_tasks = data.get("checklist_tasks", {})
        employees = data.get("employees", {})

        if checklist_id not in checklists:
            return json.dumps({"error": f"Onboarding checklist with ID '{checklist_id}' not found"})

        # Validate that at least one update parameter is provided
        if not updates and not task_updates:
            return json.dumps({
                "error": "No updates provided. At least one of 'updates' or 'task_updates' must be specified."
            })

        checklist = checklists[checklist_id]
        timestamp = "2025-12-12T12:00:00"

        # Update checklist fields if provided
        if updates and isinstance(updates, dict):
            # Validate status if being updated
            if "status" in updates:
                allowed_statuses = ["pending", "completed"]
                if updates["status"] not in allowed_statuses:
                    return json.dumps({
                        "error": f"Invalid checklist status. Allowed values: {', '.join(allowed_statuses)}"
                    })

            # Allowed fields to update
            allowed_fields = ["status"]

            for key, value in updates.items():
                if key in allowed_fields:
                    checklist[key] = value

            checklist["last_updated"] = timestamp

        # Update tasks if provided
        updated_tasks = []
        if task_updates and isinstance(task_updates, list):
            for task_update in task_updates:
                if not isinstance(task_update, dict):
                    return json.dumps({"error": "Each task_update must be a JSON object"})

                task_id = task_update.get("task_id")
                if not task_id:
                    return json.dumps({"error": "Each task_update must have a 'task_id' field"})

                task_id = str(task_id)
                if task_id not in checklist_tasks:
                    return json.dumps({"error": f"Task with ID '{task_id}' not found"})

                task = checklist_tasks[task_id]

                # Verify task belongs to this checklist
                if task.get("checklist_id") != checklist_id:
                    return json.dumps({
                        "error": f"Task '{task_id}' does not belong to checklist '{checklist_id}'"
                    })

                # Validate status if being updated
                if "status" in task_update:
                    allowed_task_statuses = ["pending", "completed"]
                    if task_update["status"] not in allowed_task_statuses:
                        return json.dumps({
                            "error": f"Invalid task status. Allowed values: {', '.join(allowed_task_statuses)}"
                        })
                    task["status"] = task_update["status"]

                # Update due_date if provided
                if "due_date" in task_update:
                    task["due_date"] = task_update["due_date"]

                # Update assigned_manager_id if provided
                if "assigned_manager_id" in task_update:
                    new_manager_id = task_update["assigned_manager_id"]
                    if new_manager_id:
                        new_manager_id = str(new_manager_id)
                        if new_manager_id not in employees:
                            return json.dumps({"error": f"Manager with ID '{new_manager_id}' not found"})
                    task["assigned_manager_id"] = new_manager_id

                # Update name if provided
                if "name" in task_update:
                    task["name"] = task_update["name"]

                task["last_updated"] = timestamp
                updated_tasks.append(task)

        # Get all tasks associated with this checklist
        all_checklist_tasks = []
        for task_id, task in checklist_tasks.items():
            if task.get("checklist_id") == checklist_id:
                all_checklist_tasks.append(task)

        return json.dumps({
            "checklist": checklist,
            "tasks_updated": len(updated_tasks),
            "tasks": all_checklist_tasks,
        })


    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_onboarding_packet",
                "description": (
                    "Updates an existing onboarding packet/checklist and its tasks. "
                    "Can update the overall checklist status and individual task details. "
                    "Returns the updated checklist with all associated tasks."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "checklist_id": {
                            "type": "string",
                            "description": "The ID of the onboarding checklist to update (required).",
                        },
                        "updates": {
                            "type": "object",
                            "description": (
                                "Optional JSON object containing checklist fields to update. "
                                "Supported fields: status."
                            ),
                            "properties": {
                                "status": {
                                    "type": "string",
                                    "description": "The checklist status. Allowed values: 'pending', 'completed'.",
                                },
                            },
                        },
                        "task_updates": {
                            "type": "array",
                            "description": (
                                "Optional list of task update objects. "
                                "Each object should have task_id and fields to update."
                            ),
                            "items": {
                                "type": "object",
                                "properties": {
                                    "task_id": {
                                        "type": "string",
                                        "description": "The ID of the task to update (required).",
                                    },
                                    "status": {
                                        "type": "string",
                                        "description": "Task status. Allowed values: 'pending', 'completed'.",
                                    },
                                    "due_date": {
                                        "type": "string",
                                        "description": "New due date in format (YYYY-MM-DD).",
                                    },
                                    "assigned_manager_id": {
                                        "type": "string",
                                        "description": "New manager ID for the task.",
                                    },
                                    "name": {
                                        "type": "string",
                                        "description": "New name for the task.",
                                    },
                                },
                            },
                        },
                    },
                    "required": ["checklist_id"],
                },
            },
        }
