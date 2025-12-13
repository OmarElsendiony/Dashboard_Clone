import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class CompleteOnboardingProcess(Tool):
    """
    Complete the onboarding process by closing the checklist.
    This tool verifies all assigned tasks have status "completed" before closing the checklist.
    """

    @staticmethod
    def invoke(data: Dict[str, Any], checklist_id: str, employee_id: str) -> str:
        """
        Complete the onboarding process by verifying all tasks are completed
        and closing the checklist.
        
        Args:
            data: Dictionary containing checklists and checklist_tasks
            checklist_id: ID of the checklist to complete
            employee_id: ID of the employee for the onboarding process
            
        Returns:
            JSON string with success status and message
        """
        
        # Validate data format
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format: 'data' must be a dict"}
            )
        
        checklists = data.get("checklists", {})
        if not isinstance(checklists, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid checklists container: expected dict at data['checklists']",
                }
            )
        
        checklist_tasks = data.get("checklist_tasks", {})
        if not isinstance(checklist_tasks, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid checklist_tasks container: expected dict at data['checklist_tasks']",
                }
            )
        
        # Validate checklist_id is provided
        if not checklist_id:
            return json.dumps(
                {"success": False, "error": "checklist_id is required"}
            )
        
        # Validate employee_id is provided
        if not employee_id:
            return json.dumps(
                {"success": False, "error": "employee_id is required"}
            )
        
        checklist_id_str = str(checklist_id)
        
        # Check if checklist exists
        if checklist_id_str not in checklists:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Checklist with ID '{checklist_id_str}' not found",
                }
            )
        
        checklist = checklists[checklist_id_str]
        
        # Validate employee_id matches the checklist's employee_id
        checklist_employee_id = checklist.get("employee_id")
        if checklist_employee_id != employee_id:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee ID mismatch: provided employee_id '{employee_id}' does not match checklist's employee_id '{checklist_employee_id}'",
                }
            )
        
        # Check if checklist is already completed
        if checklist.get("status") == "completed":
            return json.dumps(
                {
                    "success": False,
                    "error": f"Checklist '{checklist_id_str}' is already completed",
                }
            )
        
        # Get all tasks for this checklist
        tasks_for_checklist = [
            task
            for task in checklist_tasks.values()
            if task.get("checklist_id") == checklist_id_str
        ]
        
        # Check if checklist has any tasks
        if not tasks_for_checklist:
            return json.dumps(
                {
                    "success": False,
                    "error": f"No tasks found for checklist '{checklist_id_str}'",
                }
            )
        
        # Verify all tasks are completed
        incomplete_tasks = [
            task
            for task in tasks_for_checklist
            if task.get("status") != "completed"
        ]
        
        if incomplete_tasks:
            incomplete_task_names = [task.get("name", "Unknown") for task in incomplete_tasks]
            return json.dumps(
                {
                    "success": False,
                    "error": f"Cannot complete onboarding process. The following tasks are not completed: {', '.join(incomplete_task_names)}",
                }
            )
        
        # All tasks are completed, update checklist status
        timestamp = "2025-11-16T23:59:00"
        checklist["status"] = "completed"
        checklist["last_updated"] = timestamp
        
        return json.dumps(
            {
                "success": True,
                "message": f"Onboarding process for checklist '{checklist_id_str}' has been completed successfully",
                "checklist_id": checklist_id_str,
                "status": "completed",
                "employee_id": employee_id,
                "checklist_type": checklist.get("checklist_type"),
                "last_updated": timestamp,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """
        Tool schema for function-calling.
        """
        return {
            "type": "function",
            "function": {
                "name": "complete_onboarding_process",
                "description": (
                    "Complete the onboarding process by closing the checklist. "
                    "This tool verifies that all assigned tasks for the checklist have status 'completed' "
                    "before updating the checklist status to 'completed'. "
                    "If any tasks are incomplete, the operation will fail and return an error message. "
                    "Returns success status with checklist details on completion."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "checklist_id": {
                            "type": "string",
                            "description": "The ID of the checklist to complete (required)",
                        },
                        "employee_id": {
                            "type": "string",
                            "description": "The ID of the employee for the onboarding process (required)",
                        },
                    },
                    "required": ["checklist_id", "employee_id"],
                },
            },
            
        }
