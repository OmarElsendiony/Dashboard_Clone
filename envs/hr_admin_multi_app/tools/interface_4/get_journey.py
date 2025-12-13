import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class GetJourney(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        checklist_type: str,
        employee_id: str,
        checklist_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        """
        Get journey (checklist) with its tasks based on filter criteria.
        Returns checklist data along with all related checklist_tasks.
        """
        checklists = data.get("checklists", {})
        checklist_tasks = data.get("checklist_tasks", {})
        employees = data.get("employees", {})
        results = []
        
        # Validate required fields
        if not checklist_type:
            return json.dumps({
                "success": False,
                "error": "checklist_type is required"
            })
        
        if not employee_id:
            return json.dumps({
                "success": False,
                "error": "employee_id is required"
            })
        
        # Validate checklist_type
        valid_checklist_types = ["onboarding", "offboarding"]
        if checklist_type not in valid_checklist_types:
            return json.dumps({
                "success": False,
                "error": f"Invalid checklist_type. Must be one of: {', '.join(valid_checklist_types)}"
            })
        
        # Validate employee exists
        if employee_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"employee_id '{employee_id}' does not reference a valid employee"
            })
        
        # Validate status if provided
        if status:
            valid_statuses = ["pending", "completed"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                })
        
        # Build index of tasks by checklist_id for efficient lookup
        tasks_by_checklist = {}
        for task_id, task in checklist_tasks.items():
            task_checklist_id = task.get("checklist_id")
            if task_checklist_id not in tasks_by_checklist:
                tasks_by_checklist[task_checklist_id] = []
            tasks_by_checklist[task_checklist_id].append(task)
        
        # Filter checklists
        for chk_id, checklist in checklists.items():
            match = True
            
            if checklist_type and checklist.get("checklist_type") != checklist_type:
                match = False
            if employee_id and checklist.get("employee_id") != employee_id:
                match = False
            if checklist_id and chk_id != checklist_id:
                match = False
            if status and checklist.get("status") != status:
                match = False
            
            if match:
                # Create a copy of the checklist to avoid modifying the original
                journey = checklist.copy()
                
                # Add related tasks
                journey["tasks"] = tasks_by_checklist.get(chk_id, [])
                
                results.append(journey)
        
        return json.dumps({
            "success": True,
            "count": len(results),
            "journeys": results
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_journey",
                "description": "Get journey (checklist) with its tasks based on filter criteria. Returns checklist data along with all related checklist_tasks.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "checklist_type": {
                            "type": "string",
                            "description": "Type of checklist: onboarding, offboarding (required)",
                            "enum": ["onboarding", "offboarding"]
                        },
                        "employee_id": {
                            "type": "string",
                            "description": "Employee ID (required)"
                        },
                        "checklist_id": {
                            "type": "string",
                            "description": "Filter by checklist ID (optional)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by status: pending, completed (optional)",
                            "enum": ["pending", "completed"]
                        }
                    },
                    "required": ["checklist_type", "employee_id"]
                }
            }
        }
