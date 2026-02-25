import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool
from datetime import datetime

class UpdateSubtask(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        work_item_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        assignee_user_id: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
        start_date: Optional[str] = None
    ) -> str:
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
        users = data.get("users", {})
        
        if not work_item_id:
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: work_item_id is required"
            })
        
        if str(work_item_id) not in work_items:
            return json.dumps({
                "success": False,
                "error": f"Subtask with ID '{work_item_id}' not found"
            })
        
        subtask = work_items[str(work_item_id)]
        
        subtask_type = subtask.get("type")
        parent_id = subtask.get("parent_work_item_id")
        
        if subtask_type != "subtask" or parent_id is None:
            return json.dumps({
                "success": False,
                "error": f"Work item with ID '{work_item_id}' is not a subtask"
            })
        
        has_update_field = any([
            title is not None,
            description is not None,
            assignee_user_id is not None,
            status is not None,
            priority is not None,
            due_date is not None,
            start_date is not None
        ])
        
        if not has_update_field:
            return json.dumps({
                "success": False,
                "error": "At least one field to update must be provided"
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
        
        if assignee_user_id is not None and str(assignee_user_id) not in users:
            return json.dumps({
                "success": False,
                "error": f"Assignee with user_id '{assignee_user_id}' not found"
            })
        
        if status is not None:
            valid_statuses = ["open", "in_progress", "blocked","done"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
                })
        
        if priority is not None:
            valid_priorities = ["critical", "high", "medium", "low"]
            if priority not in valid_priorities:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid priority '{priority}'. Must be one of: {', '.join(valid_priorities)}"
                })
        
        updated_subtask = subtask.copy()
        
        if title is not None:
            updated_subtask["title"] = str(title)
        if description is not None:
            updated_subtask["description"] = str(description)
        if assignee_user_id is not None:
            updated_subtask["assignee_user_id"] = str(assignee_user_id)
        if status is not None:
            updated_subtask["status"] = str(status)
        if priority is not None:
            updated_subtask["priority"] = str(priority)
        if due_date is not None:
            updated_subtask["due_date"] = str(due_date)
        if start_date is not None:
            updated_subtask["start_date"] = str(start_date)
        
        updated_subtask["updated_at"] = "2026-02-11T23:59:00"
        
        work_items[str(work_item_id)] = updated_subtask
        
        # parent = work_items.get(str(parent_id), {})
        
        subtask_response = {
            "work_item_id": str(work_item_id),
            "type": "subtask",
            "title": str(updated_subtask.get("title", "")),
            "description": str(updated_subtask.get("description", "")) if updated_subtask.get("description") is not None else None,
            "parent_task_id": str(parent_id),
            "program_id": str(updated_subtask.get("project_id", "")) if updated_subtask.get("project_id") is not None else None,
            "assignee_user_id": str(updated_subtask.get("assignee_user_id", "")) if updated_subtask.get("assignee_user_id") is not None else None,
            "created_by": str(updated_subtask.get("created_by", "")) if updated_subtask.get("created_by") is not None else None,
            "status": str(updated_subtask.get("status", "")),
            "priority": str(updated_subtask.get("priority", "")),
            "due_date": str(updated_subtask.get("due_date", "")) if updated_subtask.get("due_date") is not None else None,
            "start_date": str(updated_subtask.get("start_date", "")) if updated_subtask.get("start_date") is not None else None,
            "created_at": str(updated_subtask.get("created_at", "")),
            "updated_at": str(updated_subtask.get("updated_at", ""))
            # "parent_info": {
            #     "parent_task_id": str(parent_id),
            #     "parent_title": str(parent.get("title", "")) if parent.get("title") is not None else None,
            #     "parent_type": str(parent.get("type", "")) if parent.get("type") is not None else None,
            #     "parent_status": str(parent.get("status", "")) if parent.get("status") is not None else None
            # }
        }
        
        return json.dumps({
            "success": True,
            "message": f"Subtask '{work_item_id}' updated successfully",
            "work_item_id": str(work_item_id),
            "subtask_data": subtask_response
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_subtask",
                "description": "Updates subtask details and status. Use this to change subtask assignments, update progress status, modify priorities, adjust due dates, or reflect changes in subtask scope or ownership.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "work_item_id": {
                            "type": "string",
                            "description": "The ID of the subtask to update (required, must exist and be a subtask)"
                        },
                        "title": {
                            "type": "string",
                            "description": "New title (optional)"
                        },
                        "description": {
                            "type": "string",
                            "description": "New description (optional)"
                        },
                        "assignee_user_id": {
                            "type": "string",
                            "description": "New assignee user ID (optional, must exist in users if provided)"
                        },
                        "status": {
                            "type": "string",
                            "description": "New status (optional)",
                            "enum": ["open", "in_progress", "blocked","done"]
                        },
                        "priority": {
                            "type": "string",
                            "description": "New priority (optional)",
                            "enum": ["critical", "high", "medium", "low"]
                        },
                        "due_date": {
                            "type": "string",
                            "description": "New due date in YYYY-MM-DDTHH:MM:SS format (optional)"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "New start date in YYYY-MM-DDTHH:MM:SS format (optional)"
                        }
                    },
                    "required": ["work_item_id"]
                }
            }
        }
