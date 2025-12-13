import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetOnboardingChecklist(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
    ) -> str:
        """
        Retrieve onboarding checklist(s) for a specific employee.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        # Verify employee exists
        employees = data.get("employees", {})
        if str(employee_id) not in employees:
            return json.dumps(
                {"success": False, "error": f"Employee {employee_id} not found"}
            )

        # Get all checklists
        checklists = data.get("checklists", {})
        
        # Filter onboarding checklists for this employee
        onboarding_checklists = {}
        for checklist_id, checklist in checklists.items():
            if (checklist.get("employee_id") == str(employee_id) and 
                checklist.get("checklist_type") == "onboarding"):
                onboarding_checklists[checklist_id] = checklist.copy()

        if not onboarding_checklists:
            return json.dumps(
                {
                    "success": True,
                    "message": f"No onboarding checklists found for employee {employee_id}",
                    "onboarding_checklists": {},
                    "count": 0,
                }
            )

        # Also get associated tasks if available
        checklist_tasks = data.get("checklist_tasks", {})
        tasks_by_checklist = {}
        
        for task_id, task in checklist_tasks.items():
            checklist_id = task.get("checklist_id")
            if checklist_id in onboarding_checklists:
                if checklist_id not in tasks_by_checklist:
                    tasks_by_checklist[checklist_id] = []
                tasks_by_checklist[checklist_id].append(task.copy())

        # Add tasks to each checklist
        for checklist_id in onboarding_checklists:
            onboarding_checklists[checklist_id]["tasks"] = tasks_by_checklist.get(checklist_id, [])

        return json.dumps(
            {
                "success": True,
                "message": f"Found {len(onboarding_checklists)} onboarding checklist(s) for employee {employee_id}",
                "employee_id": str(employee_id),
                "onboarding_checklists": onboarding_checklists,
                "count": len(onboarding_checklists),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_onboarding_checklist",
                "description": "Retrieves all onboarding checklists for a specific employee. Returns the checklist details including status, creation date, and associated tasks. The employee must exist in the system. If no onboarding checklists are found, an empty result is returned.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The unique identifier of the employee whose onboarding checklist(s) to retrieve. The employee must exist in the system. Required field.",
                        },
                    },
                    "required": ["employee_id"],
                },
            },
        }

