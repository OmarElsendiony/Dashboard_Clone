import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetTransitionData(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        transition_type: str,
    ) -> str:
        """
        Retrieve transition data (onboarding checklist or exit case) for an employee.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        employees = data.get("employees", {})
        
        # Validate employee exists
        if str(employee_id) not in employees:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee {employee_id} not found",
                }
            )

        # Validate transition_type
        valid_transition_types = ["onboarding_checklist", "exit_case"]
        if transition_type not in valid_transition_types:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid transition_type '{transition_type}'. Must be one of {valid_transition_types}",
                }
            )

        if transition_type == "onboarding_checklist":
            checklists = data.get("checklists", {})
            checklist_tasks = data.get("checklist_tasks", {})
            
            # Find checklist for this employee
            checklist_data = None
            for checklist_id, checklist in checklists.items():
                if checklist.get("employee_id") == str(employee_id) and checklist.get("checklist_type") == "onboarding":
                    checklist_data = checklist.copy()
                    checklist_data["checklist_id"] = checklist_id
                    
                    # Get associated tasks
                    tasks = []
                    for task_id, task in checklist_tasks.items():
                        if task.get("checklist_id") == checklist_id:
                            task_copy = task.copy()
                            task_copy["task_id"] = task_id
                            tasks.append(task_copy)
                    
                    checklist_data["tasks"] = tasks
                    break
            
            if checklist_data:
                return json.dumps(
                    {
                        "success": True,
                        "transition_type": "onboarding_checklist",
                        "data": checklist_data,
                    }
                )
            else:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"No onboarding checklist found for employee {employee_id}",
                    }
                )

        elif transition_type == "exit_case":
            exit_cases = data.get("exit_cases", {})
            
            # Find exit case for this employee
            exit_data = None
            for exit_case_id, exit_case in exit_cases.items():
                if exit_case.get("employee_id") == str(employee_id):
                    exit_data = exit_case.copy()
                    exit_data["exit_case_id"] = exit_case_id
                    break
            
            if exit_data:
                return json.dumps(
                    {
                        "success": True,
                        "transition_type": "exit_case",
                        "data": exit_data,
                    }
                )
            else:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"No exit case found for employee {employee_id}",
                    }
                )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_transition_data",
                "description": "Retrieves employee transition data from the HR system. This function can retrieve either onboarding checklist information (including all associated tasks with their status, due dates, and assigned managers) or exit case information (including reason for exit, exit date, and clearance status)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The unique identifier of the employee whose transition data is being retrieved. Required field.",
                        },
                        "transition_type": {
                            "type": "string",
                            "description": "The type of transition data to retrieve. Valid values are 'onboarding_checklist' (to retrieve onboarding checklist and tasks) or 'exit_case' (to retrieve exit/offboarding case information). Required field.",
                        },
                    },
                    "required": ["employee_id", "transition_type"],
                },
            },
        }