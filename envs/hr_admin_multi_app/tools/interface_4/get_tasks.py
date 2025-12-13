import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool

class GetTasks(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        checklist_id: str,
        employee_id: Optional[str] = None,
        name: Optional[str] = None,
        due_date: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        """
        Get task(s) from a checklist based on filter criteria.
        Returns all tasks that match the specified filters.
        """
        checklist_tasks = data.get("checklist_tasks", {})
        checklists = data.get("checklists", {})
        employees = data.get("employees", {})
        results = []
        
        # Validate required field
        if not checklist_id:
            return json.dumps({
                "success": False,
                "error": "checklist_id is required",
                "count": 0,
                "tasks": []
            })
        
        # Validate checklist exists
        if checklist_id not in checklists:
            return json.dumps({
                "success": False,
                "error": f"checklist_id '{checklist_id}' does not reference a valid checklist",
                "count": 0,
                "tasks": []
            })
        
        checklist = checklists[checklist_id]
        
        # Validate employee_id if provided
        if employee_id:
            if employee_id not in employees:
                return json.dumps({
                    "success": False,
                    "error": f"employee_id '{employee_id}' does not reference a valid employee",
                    "count": 0,
                    "tasks": []
                })
            
            # Check if checklist belongs to this employee
            if checklist.get("employee_id") != employee_id:
                return json.dumps({
                    "success": False,
                    "error": f"checklist_id '{checklist_id}' does not belong to employee_id '{employee_id}'",
                    "count": 0,
                    "tasks": []
                })
        
        # Validate status if provided
        if status:
            valid_statuses = ["pending", "completed"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                    "count": 0,
                    "tasks": []
                })
        
        # Filter tasks
        for task_id, task in checklist_tasks.items():
            match = True
            
            # checklist_id is required filter
            if task.get("checklist_id") != checklist_id:
                match = False
            
            if name and task.get("name") != name:
                match = False
            if due_date and task.get("due_date") != due_date:
                match = False
            if status and task.get("status") != status:
                match = False
            
            if match:
                # Create a copy of the task to avoid modifying the original
                task_copy = task.copy()
                results.append(task_copy)
        
        return json.dumps({
            "success": True,
            "count": len(results),
            "tasks": results
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_tasks",
                "description": "Get task(s) from a checklist based on filter criteria. Returns all tasks that match the specified filters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "checklist_id": {
                            "type": "string",
                            "description": "Checklist ID (required)"
                        },
                        "employee_id": {
                            "type": "string",
                            "description": "Filter by employee ID - validates checklist belongs to this employee (optional)"
                        },
                        "name": {
                            "type": "string",
                            "description": "Filter by task name (optional)"
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Filter by due date in YYYY-MM-DD format (optional)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by status: pending, completed (optional)",
                            "enum": ["pending", "completed"]
                        }
                    },
                    "required": ["checklist_id"]
                }
            }
        }
