import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool


class UpdateOnboardChecklist(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        checklist_id: str,
        status: Optional[str] = None,
        task_updates: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Update an onboarding checklist and/or its associated tasks.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        checklists = data.setdefault("checklists", {})
        checklist_tasks = data.setdefault("checklist_tasks", {})
        employees = data.setdefault("employees", {})
        
        # Validate checklist exists
        if str(checklist_id) not in checklists:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Onboarding checklist {checklist_id} not found",
                }
            )

        checklist = checklists[str(checklist_id)]
        
        # Validate this is an onboarding checklist
        if checklist.get("checklist_type") != "onboarding":
            return json.dumps(
                {
                    "success": False,
                    "error": f"Checklist {checklist_id} is not an onboarding checklist",
                }
            )
        
        current_time = datetime.now().isoformat()

        # Update checklist status if provided
        if status is not None:
            valid_statuses = ["pending", "completed"]
            if status not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status '{status}'. Must be one of {valid_statuses}",
                    }
                )

            # If status is being changed to "completed", validate all tasks are completed
            if status == "completed":
                all_tasks_completed = True
                for task_id, task in checklist_tasks.items():
                    if task.get("checklist_id") == str(checklist_id):
                        if task.get("status") != "completed":
                            all_tasks_completed = False
                            break

                if not all_tasks_completed:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "Cannot set checklist status to 'completed'. Not all tasks are completed.",
                        }
                    )

            checklist["status"] = status
            checklist["last_updated"] = current_time

        # Update tasks if provided
        updated_tasks = []
        if task_updates:
            for task_update in task_updates:
                task_id = task_update.get("task_id")
                
                if not task_id:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "Each task update must include 'task_id'",
                        }
                    )

                if str(task_id) not in checklist_tasks:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Task {task_id} not found",
                        }
                    )

                task = checklist_tasks[str(task_id)]

                # Verify task belongs to this checklist
                if task.get("checklist_id") != str(checklist_id):
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Task {task_id} does not belong to checklist {checklist_id}",
                        }
                    )

                # Update task fields
                if "due_date" in task_update:
                    task["due_date"] = task_update["due_date"]

                if "assigned_manager_id" in task_update:
                    manager_id = task_update["assigned_manager_id"]
                    # Validate manager exists and is active
                    if manager_id:
                        if str(manager_id) not in employees:
                            return json.dumps(
                                {
                                    "success": False,
                                    "error": f"Manager {manager_id} not found",
                                }
                            )
                        if employees[str(manager_id)].get("status") != "active":
                            return json.dumps(
                                {
                                    "success": False,
                                    "error": f"Manager {manager_id} is not active",
                                }
                            )
                    task["assigned_manager_id"] = manager_id

                if "status" in task_update:
                    task_status = task_update["status"]
                    valid_task_statuses = ["pending", "completed"]
                    if task_status not in valid_task_statuses:
                        return json.dumps(
                            {
                                "success": False,
                                "error": f"Invalid task status '{task_status}'. Must be one of {valid_task_statuses}",
                            }
                        )
                    task["status"] = task_status

                task["last_updated"] = current_time
                updated_tasks.append(task.copy())

        # Get all tasks for this checklist to return
        all_tasks = []
        for task_id, task in checklist_tasks.items():
            if task.get("checklist_id") == str(checklist_id):
                task_copy = task.copy()
                task_copy["task_id"] = task_id
                all_tasks.append(task_copy)

        return json.dumps(
            {
                "success": True,
                "message": f"Onboarding checklist {checklist_id} updated successfully",
                "checklist_data": checklist.copy(),
                "updated_tasks": updated_tasks,
                "all_tasks": all_tasks,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_onboard_checklist",
                "description": "Updates an onboarding checklist and/or its associated tasks. This function can update the overall checklist status (e.g., to 'completed' when all tasks are done) and can update individual task properties including due dates, assigned managers, and task status. When updating checklist status to 'completed', all tasks must be completed first",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "checklist_id": {
                            "type": "string",
                            "description": "The unique identifier of the onboarding checklist to update. Required field.",
                        },
                        "status": {
                            "type": "string",
                            "description": "The new status for the checklist. Valid values are 'pending' or 'completed'. When setting to 'completed', all associated tasks must have 'completed' status. Optional field.",
                        },
                        "task_updates": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "task_id": {
                                        "type": "string",
                                        "description": "The unique identifier of the task to update. Required for each task update."
                                    },
                                    "due_date": {
                                        "type": "string",
                                        "description": "The due date for the task in YYYY-MM-DD format. Typically set to employee start date per SOP 3."
                                    },
                                    "assigned_manager_id": {
                                        "type": "string",
                                        "description": "The employee ID of the manager assigned to this task. Manager must exist and have 'active' status."
                                    },
                                    "status": {
                                        "type": "string",
                                        "description": "The status of the task. Valid values are 'pending' or 'completed'."
                                    }
                                },
                                "required": ["task_id"]
                            },
                            "description": "List of task updates to apply. Each task update must include the task_id and can include due_date, assigned_manager_id, and/or status. Optional field.",
                        },
                    },
                    "required": ["checklist_id"],
                },
            },
        }