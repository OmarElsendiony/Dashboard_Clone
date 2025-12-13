import json
from typing import Any, Dict, List, Optional

from tau_bench.envs.tool import Tool


class InitiateOffboarding(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        reason: str,
        exit_date: str,
        tasks: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Initiate the offboarding process for an employee by creating an exit case
        and an offboarding checklist with tasks.
        
        Args:
            data: The database dictionary containing all tables.
            employee_id: The ID of the employee to offboard (required).
            reason: The reason for offboarding. Allowed values: 'misconduct', 'security_breach', 
                'policy_violation', 'voluntary_resignation', 'layoff' (required).
            exit_date: The exit date in format (YYYY-MM-DD) (required).
            tasks: Optional list of task objects for the offboarding checklist. Each task should have:
                name (required): Name of the offboarding task.
                due_date (required): Due date in format (YYYY-MM-DD).
                assigned_manager_id (optional): Employee ID of the manager responsible.
                If not provided, default offboarding tasks will be created.
        
        Returns:
            JSON string with the created exit case, checklist, and tasks.
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
        if not reason:
            return json.dumps({"error": "Missing required parameter: reason is required"})
        if not exit_date:
            return json.dumps({"error": "Missing required parameter: exit_date is required"})

        # Validate reason
        allowed_reasons = ["misconduct", "security_breach", "policy_violation", "voluntary_resignation", "layoff"]
        if reason not in allowed_reasons:
            return json.dumps({
                "error": f"Invalid reason. Allowed values: {', '.join(allowed_reasons)}"
            })

        employee_id = str(employee_id)
        employees = data.get("employees", {})
        exit_cases = data.get("exit_cases", {})
        checklists = data.get("checklists", {})
        checklist_tasks = data.get("checklist_tasks", {})

        if employee_id not in employees:
            return json.dumps({"error": f"Employee with ID '{employee_id}' not found"})

        # Check for existing exit case
        for exit_id, exit_case in exit_cases.items():
            if exit_case.get("employee_id") == employee_id:
                return json.dumps({
                    "error": f"Exit case for employee '{employee_id}' already exists"
                })

        # Check for existing offboarding checklist
        for checklist_id, checklist in checklists.items():
            if checklist.get("employee_id") == employee_id and checklist.get("checklist_type") == "offboarding":
                return json.dumps({
                    "error": f"Offboarding checklist for employee '{employee_id}' already exists"
                })

        employee = employees[employee_id]
        if employee.get("status") == "inactive":
            return json.dumps({"error": f"Employee '{employee_id}' is already inactive"})

        # Flag employee for high offboard risk if applicable
        if reason in ["misconduct", "security_breach", "policy_violation"]:
            employee["flag_high_offboard_risk"] = True
        employee["flag_pending_settlement"] = True
        employee["last_updated"] = "2025-11-16T23:59:00"

        # Generate new exit case ID
        exit_case_id = generate_id(exit_cases)

        # Create exit case record
        timestamp = "2025-11-16T23:59:00"
        new_exit_case = {
            "exit_case_id": exit_case_id,
            "employee_id": employee_id,
            "reason": reason,
            "exit_date": exit_date,
            "exit_clearance_status": "pending",
            "created_at": timestamp,
            "last_updated": timestamp,
        }

        exit_cases[exit_case_id] = new_exit_case
        data["exit_cases"] = exit_cases

        # Create offboarding checklist
        checklist_id = generate_id(checklists)
        new_checklist = {
            "checklist_id": checklist_id,
            "checklist_type": "offboarding",
            "employee_id": employee_id,
            "status": "pending",
            "created_at": timestamp,
            "last_updated": timestamp,
        }

        checklists[checklist_id] = new_checklist
        data["checklists"] = checklists

        # Default offboarding tasks
        default_task_names = [
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
        ]

        # Get manager_id for default task assignment
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
            # Create default offboarding tasks
            for task_name in default_task_names:
                task_id = generate_id(checklist_tasks)
                new_task = {
                    "task_id": task_id,
                    "checklist_id": checklist_id,
                    "name": task_name,
                    "due_date": exit_date,
                    "assigned_manager_id": manager_id,
                    "status": "pending",
                    "created_at": timestamp,
                    "last_updated": timestamp,
                }
                checklist_tasks[task_id] = new_task
                created_tasks.append(new_task)

        data["checklist_tasks"] = checklist_tasks

        return json.dumps({
            "exit_case": new_exit_case,
            "checklist": new_checklist,
            "tasks_created": len(created_tasks),
            "tasks": created_tasks,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "initiate_offboarding",
                "description": (
                    "Initiates the offboarding process for an employee by creating an exit case "
                    "and an offboarding checklist with tasks. "
                    "Sets appropriate flags on the employee record based on the exit reason. "
                    "If tasks are not provided, default offboarding tasks will be created."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The ID of the employee to offboard (required).",
                        },
                        "reason": {
                            "type": "string",
                            "description": (
                                "The reason for offboarding (required). "
                                "Allowed values: 'misconduct', 'security_breach', 'policy_violation', "
                                "'voluntary_resignation', 'layoff'."
                            ),
                        },
                        "exit_date": {
                            "type": "string",
                            "description": "The exit date in format (YYYY-MM-DD) (required).",
                        },
                        "tasks": {
                            "type": "array",
                            "description": (
                                "Optional list of task objects for the offboarding checklist. "
                                "If not provided, default offboarding tasks will be created. "
                                "Each task should have name, due_date, and optionally assigned_manager_id."
                            ),
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "description": "Name of the offboarding task (required).",
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
                    "required": ["employee_id", "reason", "exit_date"],
                },
            },
        }
