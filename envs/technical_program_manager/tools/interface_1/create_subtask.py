import json
from datetime import datetime
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreateSubtask(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        title: str,
        parent_task_id: str,
        program_id: str,
        description: Optional[str] = None,
        assignee_user_id: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        due_date: Optional[str] = None,
        start_date: Optional[str] = None
    ) -> str:
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(int(max(table.keys(), key=lambda x: int(x))) + 1)
            
        def validate_datetime_format(date_string: str, field_name: str) -> Optional[str]:
            try:
                datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
                return None
            except ValueError:
                return f"Invalid {field_name} format. Expected YYYY-MM-DDTHH:MM:SS, got '{date_string}'"
        
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for work_items"
            })
        
        work_items = data.get("work_items", {})
        projects = data.get("projects", {})
        users = data.get("users", {})
        
        if not title or not parent_task_id or not program_id:
            return json.dumps({
                "success": False,
                "error": "Missing parameters: title, parent_task_id, and program_id"
            })
        
        if str(parent_task_id) not in work_items:
            return json.dumps({
                "success": False,
                "error": f"Parent task with ID '{parent_task_id}' not found"
            })
        
        parent_task = work_items[str(parent_task_id)]
        
        if parent_task.get("type") != "task":
            return json.dumps({
                "success": False,
                "error": f"Parent work item must be a task, got '{parent_task.get('type')}'"
            })
        
        parent_status = parent_task.get("status")
        if parent_status not in ["open", "in_progress"]:
            return json.dumps({
                "success": False,
                "error": f"Parent task must be 'open' or 'in_progress', current status is '{parent_status}'"
            })
        
        if str(program_id) not in projects:
            return json.dumps({
                "success": False,
                "error": f"Program with ID '{program_id}' not found"
            })
        
        if parent_task.get("project_id") != str(program_id):
            return json.dumps({
                "success": False,
                "error": f"Parent task belongs to program '{parent_task.get('project_id')}', not '{program_id}'"
            })
        
        if assignee_user_id and str(assignee_user_id) not in users:
            return json.dumps({
                "success": False,
                "error": f"Assignee with user_id '{assignee_user_id}' not found"
            })
            
        if due_date is not None:
            error = validate_datetime_format(due_date, "due_date")
            if error:
                return json.dumps({
                    "success": False,
                    "error": error
                })

        if start_date is not None:
            error = validate_datetime_format(start_date, "start_date")
            if error:
                return json.dumps({
                    "success": False,
                    "error": error
                })
        
        if priority:
            valid_priorities = ["critical", "high", "medium", "low"]
            if priority not in valid_priorities:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid priority '{priority}'. Must be one of: {', '.join(valid_priorities)}"
                })
        
        if status:
            valid_statuses = ["open", "in_progress", "blocked", "done"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
                })
        
        current_user_id = None
        for uid, user in users.items():
            if user.get("role") == "technical_program_manager":
                current_user_id = str(uid)
                break
        
        new_work_item_id = generate_id(work_items)
        
        new_subtask = {
            "work_item_id": str(new_work_item_id),
            "type": "subtask",
            "title": str(title),
            "description": str(description) if description is not None else None,
            "parent_work_item_id": str(parent_task_id),
            "project_id": str(program_id),
            "sprint_id": str(parent_task.get("sprint_id", "")) if parent_task.get("sprint_id") is not None else None,
            "assignee_user_id": str(assignee_user_id) if assignee_user_id is not None else None,
            "created_by": str(current_user_id) if current_user_id is not None else None,
            "status": str(status) if status is not None else "open",
            "priority": str(priority) if priority is not None else "medium",
            "due_date": str(due_date) if due_date is not None else None,
            "start_date": str(start_date) if start_date is not None else None,
            "created_at": "2026-02-11T23:59:00",
            "updated_at": "2026-02-11T23:59:00"
        }
        
        work_items[str(new_work_item_id)] = new_subtask
        
        subtask_response = {
            "work_item_id": str(new_work_item_id),
            "type": "subtask",
            "title": str(title),
            "description": str(description) if description is not None else None,
            "parent_task_id": str(parent_task_id),
            "program_id": str(program_id),
            "sprint_id": str(parent_task.get("sprint_id", "")) if parent_task.get("sprint_id") is not None else None,
            "assignee_user_id": str(assignee_user_id) if assignee_user_id is not None else None,
            "created_by": str(current_user_id) if current_user_id is not None else None,
            "status": str(status) if status is not None else "open",
            "priority": str(priority) if priority is not None else "medium",
            "due_date": str(due_date) if due_date is not None else None,
            "start_date": str(start_date) if start_date is not None else None,
            "created_at": "2026-02-11T23:59:00",
            "updated_at": "2026-02-11T23:59:00"
        }
        
        return json.dumps({
            "success": True,
            "message": f"Subtask '{title}' created successfully",
            "work_item_id": str(new_work_item_id),
            "subtask_data": subtask_response
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_subtask",
                "description": "Creates a subtask under a parent task. Use this for detailed work breakdown, assigning granular work units, tracking sub-components of larger tasks, or decomposing complex tasks into manageable pieces.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Subtask title"
                        },
                        "parent_task_id": {
                            "type": "string",
                            "description": "Parent task ID"
                        },
                        "program_id": {
                            "type": "string",
                            "description": "Program ID the subtask belongs to"
                        },
                        "description": {
                            "type": "string",
                            "description": "Subtask description"
                        },
                        "assignee_user_id": {
                            "type": "string",
                            "description": "User ID of the assignee"
                        },
                        "priority": {
                            "type": "string",
                            "description": "Subtask priority. Valid values: critical, high, medium, low",
                            "enum": ["critical", "high", "medium", "low"]
                        },
                        "status": {
                            "type": "string",
                            "description": "Subtask status. Valid values: open, in_progress, blocked, done",
                            "enum": ["open", "in_progress", "blocked", "done"]
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Due date in YYYY-MM-DDTHH:MM:SS format"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Start date in YYYY-MM-DDTHH:MM:SS format"
                        }
                    },
                    "required": ["title", "parent_task_id", "program_id"]
                }
            }
        }