import json
from typing import Any, Dict, List

from tau_bench.envs.tool import Tool


class AssignExitTasks(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        tasks: List[Dict[str, Any]],
    ) -> str:
        """
        Assign exit tasks to responsible parties for an offboarding employee.
        Tasks are added to the employee's offboarding checklist.
        
        Args:
            data: The database dictionary containing all tables.
            employee_id: The ID of the employee being offboarded (required).
            tasks: List of task objects to assign. Each task should have:
                task_name (required): Name of the exit task.
                assigned_to (required): Employee ID of the person responsible.
                due_date (required): Due date in format (YYYY-MM-DD).
        
        Returns:
            JSON string with the assigned exit tasks.
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
        if not tasks or not isinstance(tasks, list):
            return json.dumps({"error": "Missing required parameter: tasks must be a list"})

        employee_id = str(employee_id)
        exit_cases = data.get("exit_cases", {})
        employees = data.get("employees", {})
        checklists = data.get("checklists", {})
        checklist_tasks = data.get("checklist_tasks", {})

        # Define allowed offboarding task names from the onboarding_checklist enum
        allowed_offboarding_tasks = {
            "Initiate Termination Request",
            "Collect Resignation Letter",
            "Manager Exit Approval",
            "Remove System Access",
            "Disable Email",
            "Collect Company Equipment",
            "Return Laptop",
            "Return Monitor",
            "Return Company Phone",
            "Exit Interview",
            "Final Timesheet Completion",
            "Retrieve Outstanding Expenses",
            "Terminate Benefits",
            "Final Payroll Processing",
            "Issue Final Payslip",
            "Archive Employee Files",
            "Send Exit Confirmation",
        }

        # Validate employee exists
        if employee_id not in employees:
            return json.dumps({"error": f"Employee with ID '{employee_id}' not found"})

        # Find the exit case for this employee
        exit_case = None
        exit_case_id = None
        for case_id, case in exit_cases.items():
            if case.get("employee_id") == employee_id:
                exit_case = case
                exit_case_id = case_id
                break

        if not exit_case:
            return json.dumps({
                "error": f"No exit case found for employee '{employee_id}'. Use initiate_offboarding first."
            })

        # Find the offboarding checklist for this employee
        offboarding_checklist_id = None
        for checklist_id, checklist in checklists.items():
            if (checklist.get("employee_id") == employee_id and 
                checklist.get("checklist_type") == "offboarding"):
                offboarding_checklist_id = checklist_id
                break

        if not offboarding_checklist_id:
            return json.dumps({
                "error": f"No offboarding checklist found for employee '{employee_id}'. "
                "Use initiate_offboarding to create one first."
            })

        timestamp = "2025-12-12T12:00:00"
        created_tasks = []

        for task in tasks:
            if not isinstance(task, dict):
                return json.dumps({"error": "Each task must be a JSON object"})

            task_name = task.get("task_name")
            assigned_to = task.get("assigned_to")
            due_date = task.get("due_date")

            if not task_name:
                return json.dumps({"error": "Each task must have a 'task_name' field"})
            if not assigned_to:
                return json.dumps({"error": "Each task must have an 'assigned_to' field"})
            if not due_date:
                return json.dumps({"error": "Each task must have a 'due_date' field"})

            # Validate task_name against allowed offboarding tasks
            if task_name not in allowed_offboarding_tasks:
                return json.dumps({
                    "error": f"Invalid task_name '{task_name}'. Must be a valid offboarding task from the onboarding_checklist enum."
                })

            # Validate due_date format (YYYY-MM-DD)
            try:
                parts = due_date.split("-")
                if len(parts) != 3:
                    raise ValueError()
                year, month, day = map(int, parts)
                if not (1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31):
                    raise ValueError()
            except (ValueError, AttributeError):
                return json.dumps({"error": "Invalid due_date format. Must be YYYY-MM-DD"})

            assigned_to = str(assigned_to)
            if assigned_to not in employees:
                return json.dumps({"error": f"Employee with ID '{assigned_to}' not found"})

            # Validate assigned employee is active
            assigned_employee = employees[assigned_to]
            if assigned_employee.get("status") != "active":
                return json.dumps({
                    "error": f"Employee '{assigned_to}' is not active. Cannot assign tasks to inactive employees."
                })

            task_id = generate_id(checklist_tasks)
            new_task = {
                "task_id": task_id,
                "checklist_id": offboarding_checklist_id,
                "name": task_name,
                "assigned_manager_id": assigned_to,
                "due_date": due_date,
                "status": "pending",
                "created_at": timestamp,
                "last_updated": timestamp,
            }
            checklist_tasks[task_id] = new_task
            created_tasks.append(new_task)

        data["checklist_tasks"] = checklist_tasks

        return json.dumps({
            "exit_case_id": exit_case_id,
            "employee_id": employee_id,
            "checklist_id": offboarding_checklist_id,
            "tasks_created": len(created_tasks),
            "tasks": created_tasks,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "assign_exit_tasks",
                "description": (
                    "Assigns exit tasks to responsible parties for an offboarding employee. "
                    "Tasks are added to the employee's existing offboarding checklist. "
                    "Automatically finds the employee's exit case and offboarding checklist. "
                    "Requires an offboarding checklist to exist (created via initiate_offboarding). "
                    "Task names must be valid offboarding tasks from the onboarding_checklist enum "
                    "and assigned_to must be an active employee."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The ID of the employee being offboarded (required).",
                        },
                        "tasks": {
                            "type": "array",
                            "description": (
                                "List of task objects to assign (required). "
                                "Each task should have task_name, assigned_to, and due_date."
                            ),
                            "items": {
                                "type": "object",
                                "properties": {
                                    "task_name": {
                                        "type": "string",
                                        "description": "Name of the exit task (required). Must be from the onboarding_checklist enum.",
                                    },
                                    "assigned_to": {
                                        "type": "string",
                                        "description": "Employee ID of the person responsible (required).",
                                    },
                                    "due_date": {
                                        "type": "string",
                                        "description": "Due date in format (YYYY-MM-DD) (required).",
                                    },
                                },
                            },
                        },
                    },
                    "required": ["employee_id", "tasks"],
                },
            },
        }
