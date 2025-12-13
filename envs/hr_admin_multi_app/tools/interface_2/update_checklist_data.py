import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdateChecklistData(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        checklist_id: str,
        task_id: Optional[str] = None,
        task_status: Optional[str] = None,
        assigned_manager_id: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        """
        Update checklist data or tasks in a checklist for an employee.
        This tool focuses on updating tasks in the checklist. When updating checklist status
        to 'completed', it verifies that all tasks are completed.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        # Debug: Uncomment to see what parameters are received
        import sys
        print(f"DEBUG: status={repr(status)}, type={type(status)}, task_id={task_id}, task_status={task_status}", file=sys.stderr)

        # Normalize status - handle empty strings and None
        if status is not None and isinstance(status, str) and status.strip() == "":
            status = None

        checklists = data.get("checklists", {})
        checklist_tasks = data.get("checklist_tasks", {})

        # Verify checklist exists
        if str(checklist_id) not in checklists:
            return json.dumps(
                {"success": False, "error": f"Checklist {checklist_id} not found"}
            )

        checklist = checklists[str(checklist_id)]

        # Verify employee exists
        employees = data.get("employees", {})
        if str(employee_id) not in employees:
            return json.dumps(
                {"success": False, "error": f"Employee {employee_id} not found"}
            )

        # Verify the checklist belongs to the specified employee
        if checklist.get("employee_id") != str(employee_id):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Checklist {checklist_id} does not belong to employee {employee_id}",
                }
            )

        # Track what was updated
        applied_updates = []
        
        # Early validation: Check if at least one update parameter is provided
        # Note: Check status first since it's the most common update operation
        has_update_params = (
            status is not None or
            task_id is not None or
            task_status is not None or
            assigned_manager_id is not None or
            name is not None
        )
        
        if not has_update_params:
            # Provide helpful error message
            received_params = []
            if status is not None:
                received_params.append(f"status={repr(status)}")
            if task_id is not None:
                received_params.append(f"task_id={repr(task_id)}")
            if task_status is not None:
                received_params.append(f"task_status={repr(task_status)}")
            if assigned_manager_id is not None:
                received_params.append(f"assigned_manager_id={repr(assigned_manager_id)}")
            if name is not None:
                received_params.append(f"name={repr(name)}")
            
            error_msg = "No fields to update. Please provide at least one field to update (task_id with task_status, or checklist fields like status, name, assigned_manager_id)."
            if received_params:
                error_msg += f" Received parameters: {', '.join(received_params)}"
            else:
                error_msg += " No update parameters were provided."
            
            return json.dumps(
                {
                    "success": False,
                    "error": error_msg,
                }
            )

        # Update task if task_id is provided
        if task_id is not None:
            updated_fields = []
            if str(task_id) not in checklist_tasks:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Task {task_id} not found",
                    }
                )
            
            task = checklist_tasks[str(task_id)]
            
            # Verify the task belongs to the specified checklist
            if task.get("checklist_id") != str(checklist_id):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Task {task_id} does not belong to checklist {checklist_id}",
                    }
                )
            
            # Update task status if provided
            if task_status is not None:
                valid_task_statuses = ["pending", "in_progress", "completed"]
                if task_status not in valid_task_statuses:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Invalid task status. Must be one of: {', '.join(valid_task_statuses)}",
                        }
                    )
                task["status"] = task_status
                task["last_updated"] = "2025-12-12T12:00:00"
                updated_fields.append("status")
                

            # Verify assigned_manager_id if provided
            if assigned_manager_id is not None:
                if str(assigned_manager_id) not in employees:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Assigned manager {assigned_manager_id} not found",
                        }
                    )

                task["assigned_manager_id"] = str(assigned_manager_id)
                task["last_updated"] = "2025-12-12T12:00:00"
                updated_fields.append("assigned_manager_id")
            # Record update metadata
            applied_updates.append({"target": "task", "task_id": task_id, "updated_fields": updated_fields})

        updated_fields = []
        # Update name if provided
        if name is not None:
            checklist["name"] = name
            updated_fields.append("name")

        # Update status if provided
        if status is not None:
            valid_statuses = ["pending", "in_progress", "completed"]
            if status not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                    }
                )
            
            # If trying to mark checklist as completed, verify all tasks are completed
            if status == "completed":
                # Get all tasks for this checklist
                tasks_for_checklist = [
                    task for task in checklist_tasks.values()
                    if task.get("checklist_id") == str(checklist_id)
                ]
                
                if tasks_for_checklist:
                    pending_tasks = [
                        task for task in tasks_for_checklist
                        if task.get("status") not in ["completed"]
                    ]
                    
                    if pending_tasks:
                        pending_task_ids = [task.get("task_id") for task in pending_tasks]
                        return json.dumps(
                            {
                                "success": False,
                                "error": f"Cannot mark checklist as completed. There are {len(pending_tasks)} pending task(s): {', '.join(pending_task_ids)}",
                            }
                        )
            
            checklist["status"] = status
            updated_fields.append("status")

        # Update last_updated timestamp
        checklist["last_updated"] = "2025-12-12T12:00:00"

        if not applied_updates and not updated_fields:
            return json.dumps(
                {
                    "success": False,
                    "error": "No fields to update. Please provide at least one field to update (task_id with task_status, or checklist fields).",
                }
            )
        applied_updates.append({"target": "checklist", "updated_fields": updated_fields})
        return json.dumps(
            {
                "success": True,
                "message": f"Checklist {checklist_id} updated successfully",
                "applied_updates": applied_updates,
                "checklist_data": checklist,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_checklist_data",
                "description": "Updates tasks in a checklist or checklist metadata for an employee. This tool primarily focuses on updating tasks within the checklist. When updating a task, provide task_id and task_status. When updating checklist status to 'completed', the tool verifies that all tasks in the checklist are completed - it will reject the update if any tasks are still pending. The checklist must exist and belong to the specified employee. All updates are tracked with a timestamp.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The unique identifier of the employee who owns the checklist. The employee must exist in the system. Required field.",
                        },
                        "checklist_id": {
                            "type": "string",
                            "description": "The unique identifier of the checklist to update. The checklist must exist and belong to the specified employee. Required field.",
                        },
                        "task_id": {
                            "type": "string",
                            "description": "The unique identifier of the task to update within the checklist. The task must exist and belong to the specified checklist. Optional field. Use this to update individual tasks.",
                        },
                        "task_status": {
                            "type": "string",
                            "description": "The status to set for the task. Valid values are: 'pending', 'in_progress', 'completed'. Required if task_id is provided. Optional field.",
                        },
                        "assigned_manager_id": {
                            "type": "string",
                            "description": "The employee ID of the manager who will oversee this checklist. The manager must exist in the system. Optional field.",
                        },
                        "name": {
                            "type": "string",
                            "description": "A descriptive name for the checklist. Optional field.",
                        },
                        "status": {
                            "type": "string",
                            "description": "The status of the checklist. Valid values are: 'pending', 'in_progress', 'completed'. If set to 'completed', all tasks in the checklist must be completed, otherwise the update will be rejected. Optional field.",
                        },
                    },
                    "required": ["employee_id", "checklist_id"],
                },
            },
        }