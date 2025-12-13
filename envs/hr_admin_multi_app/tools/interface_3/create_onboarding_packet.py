import json
from typing import Any, Dict, List, Optional

from tau_bench.envs.tool import Tool


class CreateOnboardingPacket(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        tasks: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Create a new onboarding packet/checklist for an employee with associated tasks.
        
        Args:
            data: The database dictionary containing all tables.
            employee_id: The ID of the employee to create onboarding packet for (required).
            tasks: Optional list of task objects to create. Each task should have:
                name (required): Name of the onboarding task.
                due_date (required): Due date in format (YYYY-MM-DD).
                assigned_manager_id (optional): Employee ID of the manager responsible.
                If not provided, default onboarding tasks will be created.
        
        Returns:
            JSON string with the created onboarding checklist and tasks.
        """
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            max_id = 0
            for k in table.keys():
                try:
                    max_id = max(max_id, int(k))
                except ValueError:
                    continue
            return str(max_id + 1)

        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not employee_id:
            return json.dumps({"error": "Missing required parameter: employee_id is required"})

        employee_id = str(employee_id)
        employees = data.get("employees", {})
        checklists = data.get("checklists", {})
        checklist_tasks = data.get("checklist_tasks", {})

        if employee_id not in employees:
            return json.dumps({"error": f"Employee with ID '{employee_id}' not found"})

        employee = employees[employee_id]

        # Check if employee already has an onboarding checklist
        for checklist_id, checklist in checklists.items():
            if checklist.get("employee_id") == employee_id and checklist.get("checklist_type") == "onboarding":
                return json.dumps({
                    "error": f"Employee '{employee_id}' already has an onboarding checklist"
                })

        # Generate new checklist ID
        checklist_id = generate_id(checklists)

        # Create onboarding checklist record
        timestamp = "2025-12-12T12:00:00"
        new_checklist = {
            "checklist_id": checklist_id,
            "checklist_type": "onboarding",
            "employee_id": employee_id,
            "status": "pending",
            "created_at": timestamp,
            "last_updated": timestamp,
        }

        checklists[checklist_id] = new_checklist
        data["checklists"] = checklists

        # Default onboarding tasks if not provided
        default_task_names = [
            "Collect Personal Information",
            "Complete Tax Forms (W-4, State)",
            "Verify I-9 Documents",
            "Upload ID & Eligibility Documents",
            "Direct Deposit Setup",
            "Review Employee Handbook",
            "Sign Policies",
            "IT Equipment Setup",
            "System Access Provisioning",
            "Account Creation & Credentials Setup",
            "Email Setup",
            "Badge/ID Card Generation",
            "Workstation Setup",
            "HR Policy Review",
            "Benefits Enrollment Kickoff",
            "Orientation & Welcome Session Scheduling",
            "Manager Introduction",
            "Team Introduction",
            "Required Training Assigned",
            "Set 30/60/90 Day Goals",
        ]

        # Get employee's start_date for default due_date
        default_due_date = employee.get("start_date", "2025-12-12")
        manager_id = employee.get("manager_id")

        created_tasks = []

        if tasks and isinstance(tasks, list):
            # Create custom tasks
            for task in tasks:
                if not isinstance(task, dict):
                    return json.dumps({"error": "Each task must be a JSON object"})

                task_name = task.get("name")
                due_date = task.get("due_date")
                assigned_manager_id = task.get("assigned_manager_id")

                if not task_name:
                    return json.dumps({"error": "Each task must have a 'name' field"})
                if not due_date:
                    return json.dumps({"error": "Each task must have a 'due_date' field"})

                # Validate assigned_manager_id if provided
                if assigned_manager_id:
                    assigned_manager_id = str(assigned_manager_id)
                    if assigned_manager_id not in employees:
                        return json.dumps({"error": f"Manager with ID '{assigned_manager_id}' not found"})

                task_id = generate_id(checklist_tasks)
                new_task = {
                    "task_id": task_id,
                    "checklist_id": checklist_id,
                    "name": task_name,
                    "due_date": due_date,
                    "assigned_manager_id": assigned_manager_id,
                    "status": "pending",
                    "created_at": timestamp,
                    "last_updated": timestamp,
                }
                checklist_tasks[task_id] = new_task
                created_tasks.append(new_task)
        else:
            # Create default onboarding tasks
            for task_name in default_task_names:
                task_id = generate_id(checklist_tasks)
                new_task = {
                    "task_id": task_id,
                    "checklist_id": checklist_id,
                    "name": task_name,
                    "due_date": default_due_date,
                    "assigned_manager_id": manager_id,
                    "status": "pending",
                    "created_at": timestamp,
                    "last_updated": timestamp,
                }
                checklist_tasks[task_id] = new_task
                created_tasks.append(new_task)

        data["checklist_tasks"] = checklist_tasks

        return json.dumps({
            "checklist": new_checklist,
            "tasks_created": len(created_tasks),
            "tasks": created_tasks,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_onboarding_packet",
                "description": (
                    "Creates a new onboarding packet/checklist for an employee with associated tasks. "
                    "Each employee can only have one onboarding checklist. "
                    "The checklist starts with status 'pending'. "
                    "If tasks are not provided, default onboarding tasks will be created."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The ID of the employee to create onboarding packet for (required).",
                        },
                        "tasks": {
                            "type": "array",
                            "description": (
                                "Optional list of task objects to create. "
                                "If not provided, default onboarding tasks will be created. "
                                "Each task should have name, due_date, and optionally assigned_manager_id."
                            ),
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "description": "Name of the onboarding task (required).",
                                    },
                                    "due_date": {
                                        "type": "string",
                                        "description": "Due date in format (YYYY-MM-DD) (required).",
                                    },
                                    "assigned_manager_id": {
                                        "type": "string",
                                        "description": "Employee ID of the manager responsible (optional).",
                                    },
                                },
                            },
                        },
                    },
                    "required": ["employee_id"],
                },
            },
        }
