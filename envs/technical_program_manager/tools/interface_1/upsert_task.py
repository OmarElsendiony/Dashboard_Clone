import json
from datetime import datetime
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpsertTask(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        work_item_id: Optional[str] = None,
        title: Optional[str] = None,
        program_id: Optional[str] = None,
        description: Optional[str] = None,
        assignee_user_id: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
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

        is_update = False
        existing_task = None

        if work_item_id:
            if str(work_item_id) not in work_items:
                return json.dumps({
                    "success": False,
                    "error": f"Work item with ID '{work_item_id}' not found"
                })
            
            existing_task = work_items[str(work_item_id)]
            
            if existing_task.get("type") != "task":
                return json.dumps({
                    "success": False,
                    "error": f"Work item '{work_item_id}' is not a task"
                })
            
            is_update = True

        if program_id is not None and str(program_id) not in projects:
            return json.dumps({
                "success": False,
                "error": f"Program with ID '{program_id}' not found"
            })

        if assignee_user_id is not None and str(assignee_user_id) not in users:
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

        if priority is not None:
            valid_priorities = ["critical", "high", "medium", "low"]
            if priority not in valid_priorities:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid priority '{priority}'. Must be one of: {', '.join(valid_priorities)}"
                })

        if status is not None:
            valid_statuses = ["open", "in_progress", "blocked","done"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
                })

        if is_update:
            has_update_field = any([
                title is not None,
                program_id is not None,
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
                    "error": "At least one field must be provided for update"
                })
                
            check_title = title if title is not None else existing_task.get("title")
            check_program_id = program_id if program_id is not None else existing_task.get("project_id")
            
            if title is not None or program_id is not None:
                for wid, item in work_items.items():
                    if (str(wid) != str(work_item_id) and 
                        item.get("type") == "task" and 
                        item.get("title") == check_title and 
                        str(item.get("project_id")) == str(check_program_id)):
                        return json.dumps({
                            "success": False,
                            "error": f"Task with title '{check_title}' already exists in program '{check_program_id}'"
                        })

            updated_task = {
                "work_item_id": str(work_item_id),
                "type": "task",
                "title": str(title) if title is not None else str(existing_task.get("title", "")),
                "description": str(description) if description is not None else (str(existing_task.get("description", "")) if existing_task.get("description") is not None else None),
                "parent_work_item_id": None,
                "project_id": str(program_id) if program_id is not None else str(existing_task.get("project_id", "")),
                "sprint_id": str(existing_task.get("sprint_id", "")) if existing_task.get("sprint_id") is not None else None,
                "assignee_user_id": str(assignee_user_id) if assignee_user_id is not None else (str(existing_task.get("assignee_user_id", "")) if existing_task.get("assignee_user_id") is not None else None),
                "created_by": str(existing_task.get("created_by", "")) if existing_task.get("created_by") is not None else None,
                "status": str(status) if status is not None else str(existing_task.get("status", "open")),
                "priority": str(priority) if priority is not None else str(existing_task.get("priority", "medium")),
                "due_date": str(due_date) if due_date is not None else (str(existing_task.get("due_date", "")) if existing_task.get("due_date") is not None else None),
                "start_date": str(start_date) if start_date is not None else (str(existing_task.get("start_date", "")) if existing_task.get("start_date") is not None else None),
                "created_at": str(existing_task.get("created_at", "2026-02-11T23:59:00")),
                "updated_at": "2026-02-11T23:59:00"
            }

            work_items[str(work_item_id)] = updated_task

            task_response = {
                "work_item_id": str(work_item_id),
                "type": "task",
                "title": str(updated_task.get("title", "")),
                "description": str(updated_task.get("description", "")) if updated_task.get("description") is not None else None,
                "program_id": str(updated_task.get("project_id", "")) if updated_task.get("project_id") is not None else None,
                "assignee_user_id": str(updated_task.get("assignee_user_id", "")) if updated_task.get("assignee_user_id") is not None else None,
                "created_by": str(updated_task.get("created_by", "")) if updated_task.get("created_by") is not None else None,
                "status": str(updated_task.get("status", "")),
                "priority": str(updated_task.get("priority", "")),
                "due_date": str(updated_task.get("due_date", "")) if updated_task.get("due_date") is not None else None,
                "start_date": str(updated_task.get("start_date", "")) if updated_task.get("start_date") is not None else None,
                "created_at": str(updated_task.get("created_at", "")),
                "updated_at": str(updated_task.get("updated_at", ""))
            }

            return json.dumps({
                "success": True,
                "message": f"Task '{work_item_id}' updated successfully",
                "work_item_id": str(work_item_id),
                "task_data": task_response
            })

        else:
            if not title or not program_id:
                return json.dumps({
                    "success": False,
                    "error": "Missing parameters for creation: title and program_id"
                })

            for item in work_items.values():
                if (item.get("type") == "task" and 
                    item.get("title") == title and 
                    str(item.get("project_id")) == str(program_id)):
                    return json.dumps({
                        "success": False,
                        "error": f"Task with title '{title}' already exists in program '{program_id}'"
                    })

            current_user_id = None
            for uid, user in users.items():
                if user.get("role") == "technical_program_manager":
                    current_user_id = str(uid)
                    break

            new_work_item_id = generate_id(work_items)

            new_task = {
                "work_item_id": str(new_work_item_id),
                "type": "task",
                "title": str(title),
                "description": str(description) if description is not None else None,
                "parent_work_item_id": None,
                "project_id": str(program_id),
                "sprint_id": None,
                "assignee_user_id": str(assignee_user_id) if assignee_user_id is not None else None,
                "created_by": str(current_user_id) if current_user_id is not None else None,
                "status": str(status) if status is not None else "open",
                "priority": str(priority) if priority is not None else "medium",
                "due_date": str(due_date) if due_date is not None else None,
                "start_date": str(start_date) if start_date is not None else None,
                "created_at": "2026-02-11T23:59:00",
                "updated_at": "2026-02-11T23:59:00"
            }

            work_items[str(new_work_item_id)] = new_task

            task_response = {
                "work_item_id": str(new_work_item_id),
                "type": "task",
                "title": str(new_task.get("title", "")),
                "description": str(new_task.get("description", "")) if new_task.get("description") is not None else None,
                "program_id": str(new_task.get("project_id", "")) if new_task.get("project_id") is not None else None,
                "assignee_user_id": str(new_task.get("assignee_user_id", "")) if new_task.get("assignee_user_id") is not None else None,
                "created_by": str(new_task.get("created_by", "")) if new_task.get("created_by") is not None else None,
                "status": str(new_task.get("status", "")),
                "priority": str(new_task.get("priority", "")),
                "due_date": str(new_task.get("due_date", "")) if new_task.get("due_date") is not None else None,
                "start_date": str(new_task.get("start_date", "")) if new_task.get("start_date") is not None else None,
                "created_at": str(new_task.get("created_at", "")),
                "updated_at": str(new_task.get("updated_at", ""))
            }

            return json.dumps({
                "success": True,
                "message": f"Task '{title}' created successfully",
                "work_item_id": str(new_work_item_id),
                "task_data": task_response
            })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "upsert_task",
                "description": "Creates a new task or updates an existing one. Use this to decompose project work, update task assignments, modify progress status, adjust priorities, or track work execution.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "work_item_id": {
                            "type": "string",
                            "description": "[UPDATE only] ID of the task to update."
                        },
                        "title": {
                            "type": "string",
                            "description": "[CREATION required, UPDATE optional] Task title. Must be unique within the program."
                        },
                        "program_id": {
                            "type": "string",
                            "description": "[CREATION required, UPDATE optional] ID of the program this task belongs to."
                        },
                        "description": {
                            "type": "string",
                            "description": "[CREATION optional, UPDATE optional] Task description."
                        },
                        "assignee_user_id": {
                            "type": "string",
                            "description": "[CREATION optional, UPDATE optional] User ID of the person assigned to this task."
                        },
                        "priority": {
                            "type": "string",
                            "description": "[CREATION optional, UPDATE optional] Task priority. Defaults to 'medium' on creation.",
                            "enum": ["critical", "high", "medium", "low"]
                        },
                        "status": {
                            "type": "string",
                            "description": "[CREATION optional, UPDATE optional] Task status. Defaults to 'open' on creation.",
                            "enum": ["open", "in_progress", "blocked", "done"]
                        },
                        "start_date": {
                            "type": "string",
                            "description": "[CREATION optional, UPDATE optional] Task start date in YYYY-MM-DDTHH:MM:SS format."
                        },
                        "due_date": {
                            "type": "string",
                            "description": "[CREATION optional, UPDATE optional] Task due date in YYYY-MM-DDTHH:MM:SS format."
                        }
                    },
                    "required": [],
                    "oneOf": [
                        {
                            "required": ["work_item_id"]
                        },
                        {
                            "required": ["title", "program_id"]
                        }
                    ]
                }
            }
        }