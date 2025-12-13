import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpdateOnboardingJourney(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        checklist_id: str,
        task_id: Optional[str] = None,
        status: Optional[str] = None,
        journey_status: Optional[str] = None
    ) -> str:
        """
        Update an onboarding journey (checklist) or a task within it.
        Can update task status or journey status.
        """
        checklists = data.get("checklists", {})
        checklist_tasks = data.get("checklist_tasks", {})
        timestamp = "2025-11-16T23:59:00"
        
        # Validate required parameter
        if not checklist_id:
            return json.dumps({
                "success": False,
                "error": "checklist_id is required"
            })
        
        # Validate checklist exists
        if checklist_id not in checklists:
            return json.dumps({
                "success": False,
                "error": f"checklist_id '{checklist_id}' does not reference a valid checklist"
            })
        
        checklist = checklists[checklist_id]
        
        # Validate checklist is onboarding type
        if checklist.get("checklist_type") != "onboarding":
            return json.dumps({
                "success": False,
                "error": f"checklist_id '{checklist_id}' is not an onboarding journey"
            })
        
        # Check if at least one field is being updated
        if task_id is None and status is None and journey_status is None:
            return json.dumps({
                "success": False,
                "error": "At least one of task_id, status, or journey_status must be provided to update"
            })
        
        # If task_id is provided, update the task
        if task_id is not None:
            if task_id not in checklist_tasks:
                return json.dumps({
                    "success": False,
                    "error": f"task_id '{task_id}' does not reference a valid task"
                })
            
            task = checklist_tasks[task_id]
            
            # Validate task belongs to this checklist
            if task.get("checklist_id") != checklist_id:
                return json.dumps({
                    "success": False,
                    "error": f"task_id '{task_id}' does not belong to checklist_id '{checklist_id}'"
                })
            
            # Update task status if provided
            if status is not None:
                valid_statuses = ["pending", "completed"]
                if status not in valid_statuses:
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                    })
                task["status"] = status
                task["last_updated"] = timestamp
        
        # Update journey status if provided
        if journey_status is not None:
            valid_journey_statuses = ["pending", "completed"]
            if journey_status not in valid_journey_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid journey_status. Must be one of: {', '.join(valid_journey_statuses)}"
                })
            checklist["status"] = journey_status
            checklist["last_updated"] = timestamp
        
        # Prepare response
        response = {
            "success": True,
            "checklist": checklist
        }
        
        # Include task if it was updated
        if task_id is not None:
            response["task"] = checklist_tasks[task_id]
        
        return json.dumps(response)
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_onboarding_journey",
                "description": "Update an onboarding journey (checklist) or a task within it. Can update task status (with task_id) or journey status (journey_status).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "checklist_id": {
                            "type": "string",
                            "description": "Checklist ID to update (required)"
                        },
                        "task_id": {
                            "type": "string",
                            "description": "Task ID to update (optional, required if updating task status)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Task status: pending, completed (optional, requires task_id)",
                            "enum": ["pending", "completed"]
                        },
                        "journey_status": {
                            "type": "string",
                            "description": "Journey/checklist status: pending, completed (optional)",
                            "enum": ["pending", "completed"]
                        }
                    },
                    "required": ["checklist_id"]
                }
            }
        }
