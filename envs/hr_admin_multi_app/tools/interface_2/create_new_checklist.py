import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateNewChecklist(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        checklist_type: str,
        name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        """
        Create a new checklist for employee onboarding or offboarding.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        # Validate checklist_type
        valid_types = ["onboarding", "offboarding"]
        if checklist_type not in valid_types:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid checklist_type. Must be one of: {', '.join(valid_types)}",
                }
            )

        # Verify employee exists
        employees = data.get("employees", {})
        if str(employee_id) not in employees:
            return json.dumps(
                {"success": False, "error": f"Employee {employee_id} not found"}
            )


        # Validate status if provided
        if status is not None:
            valid_statuses = ["pending", "in_progress", "completed"]
            if status not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                    }
                )
        else:
            status = "pending"  # Default status

        # Get checklists and generate new checklist_id
        checklists = data.get("checklists", {})
        if checklists:
            max_id = max(int(cid) for cid in checklists.keys())
            new_checklist_id = str(max_id + 1)
        else:
            new_checklist_id = "1"

        # Create new checklist
        new_checklist = {
            "checklist_id": new_checklist_id,
            "checklist_type": checklist_type,
            "employee_id": str(employee_id),
            "status": status,
            "created_at": "2025-12-12T12:00:00",
            "last_updated": "2025-12-12T12:00:00",
        }

        # Add name if provided (although not in the standard schema)
        if name is not None:
            new_checklist["name"] = name

        # Add to checklists
        checklists[new_checklist_id] = new_checklist
        # Add default tasks based on checklist_type (if any)
        onboarding_tasks = {
            "1": "HR Documentation & Compliance Forms",
            "2": "Workstation Setup",
            "3": "Safety Training",
            "4": "Orientation Session",
            "5": "Manager Introduction",
        }
        offboarding_tasks = {
            "1": "Initiate Termination Request",
            "2": "Collect Resignation Letter",
            "3": "Manager Exit Approval",
            "4": "Exit Interview",
        }
        checklist_tasks = data.get("checklist_tasks", {})
        tasks_to_add = (
            onboarding_tasks if checklist_type == "onboarding" else offboarding_tasks
        )
        for task_num, task_name in tasks_to_add.items():
            new_task_id = (
                str(max(int(tid) for tid in checklist_tasks.keys()) + 1)
                if checklist_tasks
                else "1"
            )
            checklist_tasks[new_task_id] = {
                "task_id": new_task_id,
                "assigned_manager_id": None,
                "checklist_id": new_checklist_id,
                "name": task_name,
                "status": "pending",
                "due_date": None,
                "created_at": "2025-12-12T12:00:00",
                "last_updated": "2025-12-12T12:00:00",
            }

        # Get tasks associated with this checklist
        tasks = [
            task for task in checklist_tasks.values()
            if task.get("checklist_id") == new_checklist_id
        ]


        return json.dumps(
            {
                "success": True,
                "message": f"Checklist {new_checklist_id} created successfully for employee {employee_id}",
                "checklist_id": new_checklist_id,
                "checklist_data": new_checklist,
                "tasks": tasks,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_new_checklist",
                "description": "Creates a new checklist for employee onboarding or offboarding processes. The checklist tracks tasks and activities that need to be completed during the employee lifecycle. The employee must exist in the system. You can optionally assign a manager to oversee the checklist.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The unique identifier of the employee for whom the checklist is being created. The employee must exist in the system. Required field.",
                        },
                        "checklist_type": {
                            "type": "string",
                            "description": "The type of checklist to create. Valid values are 'onboarding' for new employee onboarding processes, or 'offboarding' for employee exit processes. Required field.",
                        },
                        "name": {
                            "type": "string",
                            "description": "A descriptive name for the checklist. Optional field.",
                        },
                        "status": {
                            "type": "string",
                            "description": "The initial status of the checklist. Valid values are: 'pending', 'in_progress', 'completed'. If not specified, defaults to 'pending'. Optional field.",
                        },
                    },
                    "required": ["employee_id", "checklist_type"],
                },
            },
        }