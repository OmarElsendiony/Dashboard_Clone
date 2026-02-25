import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class FetchWorkItem(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        work_item_id: Optional[str] = None,
        title: Optional[str] = None,
        program_id: Optional[str] = None,
        work_item_type: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for work_items"
            })
        
        work_items = data.get("work_items", {})
        
        if not work_item_id and not title and not program_id:
            return json.dumps({
                "success": False,
                "error": "At least one parameter (work_item_id, title, or program_id) must be provided"
            })
            
        if work_item_type and work_item_type not in ["task", "subtask"]:
            return json.dumps({
                "success": False,
                "error": f"Invalid work_item_type '{work_item_type}'. Must be 'task' or 'subtask'"
            })
        
        if work_item_id:
            if str(work_item_id) not in work_items:
                return json.dumps({
                    "success": False,
                    "error": f"Work item with ID '{work_item_id}' not found"
                })
            
            found_item = work_items[str(work_item_id)]
            db_type = found_item.get("type")
            
            if db_type not in ["task", "subtask"]:
                return json.dumps({
                    "success": False,
                    "error": f"Work item '{work_item_id}' is not a task or subtask"
                })
                
            if work_item_type and db_type != work_item_type:
                return json.dumps({
                    "success": False,
                    "error": f"Work item '{work_item_id}' is of type '{db_type}', not '{work_item_type}'"
                })
                
            if program_id and str(found_item.get("project_id")) != str(program_id):
                return json.dumps({
                    "success": False,
                    "error": f"Work item does not belong to program '{program_id}'"
                })
                
            if title and str(found_item.get("title")) != str(title):
                return json.dumps({
                    "success": False,
                    "error": f"Work item title is '{found_item.get('title')}', not '{title}'"
                })
            
            work_item_data = {
                "work_item_id": str(work_item_id),
                "type": str(db_type),
                "title": str(found_item.get("title", "")),
                "description": str(found_item.get("description", "")) if found_item.get("description") is not None else None,
                "program_id": str(found_item.get("project_id", "")) if found_item.get("project_id") is not None else None,
                "assignee_user_id": str(found_item.get("assignee_user_id", "")) if found_item.get("assignee_user_id") is not None else None,
                "created_by": str(found_item.get("created_by", "")) if found_item.get("created_by") is not None else None,
                "status": str(found_item.get("status", "")),
                "priority": str(found_item.get("priority", "")),
                "due_date": str(found_item.get("due_date", "")) if found_item.get("due_date") is not None else None,
                "start_date": str(found_item.get("start_date", "")) if found_item.get("start_date") is not None else None,
                "created_at": str(found_item.get("created_at", "")),
                "updated_at": str(found_item.get("updated_at", ""))
            }
            
            if db_type == "task":
                subtask_count = sum(
                    1 for w_id, wi in work_items.items()
                    if str(wi.get("parent_work_item_id")) == str(work_item_id)
                    and wi.get("type") == "subtask"
                )
                work_item_data["subtask_count"] = int(subtask_count)
            else:
                parent_id = found_item.get("parent_work_item_id")
                work_item_data["parent_work_item_id"] = str(parent_id) if parent_id is not None else None
                if parent_id is not None:
                    parent = work_items.get(str(parent_id), {})
                    work_item_data["parent_info"] = {
                        "parent_work_item_id": str(parent_id),
                        "parent_title": str(parent.get("title", "")) if parent.get("title") is not None else None,
                        "parent_type": str(parent.get("type", "")) if parent.get("type") is not None else None,
                        "parent_status": str(parent.get("status", "")) if parent.get("status") is not None else None
                    }
            
            return json.dumps({
                "success": True,
                "work_item_data": work_item_data
            })
            
        else:
            found_items = []
            
            for wid, work_item in work_items.items():
                db_type = work_item.get("type")
                
                if db_type not in ["task", "subtask"]:
                    continue
                
                if work_item_type and db_type != work_item_type:
                    continue
                    
                if program_id and str(work_item.get("project_id")) != str(program_id):
                    continue
                    
                if title and str(work_item.get("title")) != str(title):
                    continue
                
                work_item_data = {
                    "work_item_id": str(wid),
                    "type": str(db_type),
                    "title": str(work_item.get("title", "")),
                    "description": str(work_item.get("description", "")) if work_item.get("description") is not None else None,
                    "program_id": str(work_item.get("project_id", "")) if work_item.get("project_id") is not None else None,
                    "assignee_user_id": str(work_item.get("assignee_user_id", "")) if work_item.get("assignee_user_id") is not None else None,
                    "created_by": str(work_item.get("created_by", "")) if work_item.get("created_by") is not None else None,
                    "status": str(work_item.get("status", "")),
                    "priority": str(work_item.get("priority", "")),
                    "due_date": str(work_item.get("due_date", "")) if work_item.get("due_date") is not None else None,
                    "start_date": str(work_item.get("start_date", "")) if work_item.get("start_date") is not None else None,
                    "created_at": str(work_item.get("created_at", "")),
                    "updated_at": str(work_item.get("updated_at", ""))
                }
                
                if db_type == "task":
                    subtask_count = sum(
                        1 for w_id, wi in work_items.items()
                        if str(wi.get("parent_work_item_id")) == str(wid)
                        and wi.get("type") == "subtask"
                    )
                    work_item_data["subtask_count"] = int(subtask_count)
                else:
                    parent_id = work_item.get("parent_work_item_id")
                    work_item_data["parent_work_item_id"] = str(parent_id) if parent_id is not None else None
                    if parent_id is not None:
                        parent = work_items.get(str(parent_id), {})
                        work_item_data["parent_info"] = {
                            "parent_work_item_id": str(parent_id),
                            "parent_title": str(parent.get("title", "")) if parent.get("title") is not None else None,
                            "parent_type": str(parent.get("type", "")) if parent.get("type") is not None else None,
                            "parent_status": str(parent.get("status", "")) if parent.get("status") is not None else None
                        }
                
                found_items.append(work_item_data)
                
            if not found_items:
                search_target = work_item_type if work_item_type else "task or subtask"
                return json.dumps({
                    "success": False,
                    "error": f"No {search_target} found matching the specified filters"
                })
                
            if len(found_items) == 1:
                return json.dumps({
                    "success": True,
                    "work_item_data": found_items[0]
                })
                
            return json.dumps({
                "success": True,
                "multiple_results": True,
                "count": int(len(found_items)),
                "work_items": found_items
            })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_work_item",
                "description": "Retrieves work items (tasks or subtasks). Can fetch a single item by ID or title, or list all tasks/subtasks in a program by providing program_id.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "work_item_id": {
                            "type": "string",
                            "description": "The unique identifier of the work item"
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the work item"
                        },
                        "program_id": {
                            "type": "string",
                            "description": "Filter results by program ID. Lists all matching work items in the program"
                        },
                        "work_item_type": {
                            "type": "string",
                            "description": "Filter by work item type. Valid values: task, subtask",
                            "enum": ["task", "subtask"]
                        }
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["work_item_id"]},
                        {"required": ["title"]},
                        {"required": ["program_id"]}
                    ]
                }
            }
        }