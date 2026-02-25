import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpsertProgram(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        program_id: Optional[str] = None,
        program_key: Optional[str] = None,
        program_name: Optional[str] = None,
        program_owner_user_id: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(int(max(table.keys(), key=lambda x: int(x))) + 1)
        
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for projects"
            })
        
        projects = data.get("projects", {})
        users = data.get("users", {})
        
        existing_project = None
        existing_id = None
        is_update = False
        
        if program_id and str(program_id) in projects:
            existing_project = projects[str(program_id)]
            existing_id = str(program_id)
            is_update = True
        elif program_key:
            for pid, project in projects.items():
                if project.get("project_key") == str(program_key):
                    existing_project = project
                    existing_id = str(pid)
                    is_update = True
                    break
        
        if is_update:
            has_update_field = any([
                program_key is not None,
                program_name is not None,
                program_owner_user_id is not None,
                description is not None,
                status is not None
            ])
            
            if not has_update_field:
                return json.dumps({
                    "success": False,
                    "error": "At least one field must be provided for update: program_key, program_name, program_owner_user_id, description, or status"
                })
            
            if program_owner_user_id is not None and str(program_owner_user_id) not in users:
                return json.dumps({
                    "success": False,
                    "error": f"Program owner with user_id '{program_owner_user_id}' not found"
                })
            
            if status is not None:
                valid_statuses = ["open", "in_progress", "blocked", "closed"]
                if status not in valid_statuses:
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
                    })
            
            if program_key is not None and str(program_key) != existing_project.get("project_key"):
                for pid, project in projects.items():
                    if pid != existing_id and project.get("project_key") == str(program_key):
                        return json.dumps({
                            "success": False,
                            "error": f"Program with key '{program_key}' already exists"
                        })
            
            if program_name is not None and str(program_name) != existing_project.get("project_name"):
                for pid, project in projects.items():
                    if pid != existing_id and project.get("project_name") == str(program_name):
                        return json.dumps({
                            "success": False,
                            "error": f"Program with name '{program_name}' already exists"
                        })
            
            updated_project = {
                "project_id": str(existing_id),
                "project_key": str(program_key) if program_key is not None else str(existing_project.get("project_key", "")),
                "project_name": str(program_name) if program_name is not None else str(existing_project.get("project_name", "")),
                "description": str(description) if description is not None else (str(existing_project.get("description", "")) if existing_project.get("description") is not None else None),
                "status": str(status) if status is not None else str(existing_project.get("status", "open")),
                "project_owner_user_id": str(program_owner_user_id) if program_owner_user_id is not None else str(existing_project.get("project_owner_user_id", "")),
                "created_at": str(existing_project.get("created_at", "2026-02-11T23:59:00")),
                "updated_at": "2026-02-11T23:59:00",
                "closed_at": "2026-02-11T23:59:00" if status == "closed" and existing_project.get("status") != "closed" else (str(existing_project.get("closed_at", "")) if existing_project.get("closed_at") is not None else None)
            }
            
            projects[existing_id] = updated_project
            
            response_data = {
                "program_id": str(existing_id),
                "program_key": updated_project["project_key"],
                "program_name": updated_project["project_name"],
                "description": updated_project["description"],
                "status": updated_project["status"],
                "program_owner_user_id": updated_project["project_owner_user_id"],
                "created_at": updated_project["created_at"],
                "updated_at": updated_project["updated_at"],
                "closed_at": updated_project["closed_at"]
            }
            
            return json.dumps({
                "success": True,
                "message": f"Program '{updated_project['project_name']}' updated successfully",
                "program_id": str(existing_id),
                "program_data": response_data
            })
        
        else:
            if not program_key or not program_name or not program_owner_user_id:
                return json.dumps({
                    "success": False,
                    "error": "Missing parameters for creation: program_key, program_name, and program_owner_user_id"
                })
            
            if str(program_owner_user_id) not in users:
                return json.dumps({
                    "success": False,
                    "error": f"Program owner with user_id '{program_owner_user_id}' not found"
                })
            
            for project in projects.values():
                if project.get("project_key") == str(program_key):
                    return json.dumps({
                        "success": False,
                        "error": f"Program with key '{program_key}' already exists"
                    })
            
            for project in projects.values():
                if project.get("project_name") == str(program_name):
                    return json.dumps({
                        "success": False,
                        "error": f"Program with name '{program_name}' already exists"
                    })
            
            if status is not None:
                valid_statuses = ["open", "in_progress", "blocked", "closed"]
                if status not in valid_statuses:
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
                    })
            
            new_project_id = generate_id(projects)
            
            new_project = {
                "project_id": str(new_project_id),
                "project_key": str(program_key),
                "project_name": str(program_name),
                "description": str(description) if description is not None else None,
                "status": str(status) if status is not None else "open",
                "project_owner_user_id": str(program_owner_user_id),
                "created_at": "2026-02-11T23:59:00",
                "updated_at": "2026-02-11T23:59:00",
                "closed_at": "2026-02-11T23:59:00" if status == "closed" else None
            }
            
            projects[str(new_project_id)] = new_project
            
            response_data = {
                "program_id": str(new_project_id),
                "program_key": new_project["project_key"],
                "program_name": new_project["project_name"],
                "description": new_project["description"],
                "status": new_project["status"],
                "program_owner_user_id": new_project["project_owner_user_id"],
                "created_at": new_project["created_at"],
                "updated_at": new_project["updated_at"],
                "closed_at": new_project["closed_at"]
            }
            
            return json.dumps({
                "success": True,
                "message": f"Program '{program_name}' created successfully",
                "program_id": str(new_project_id),
                "program_data": response_data
            })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "upsert_program",
                "description": "Creates a new program or updates an existing one. Use this to create new programs, update program details, modify status, or change program ownership.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "program_id": {
                            "type": "string",
                            "description": "[UPDATE only] Unique identifier of the program to update."
                        },
                        "program_key": {
                            "type": "string",
                            "description": "[CREATION required, UPDATE optional] Unique short key for the program."
                        },
                        "program_name": {
                            "type": "string",
                            "description": "[CREATION required, UPDATE optional] Full name of the program."
                        },
                        "program_owner_user_id": {
                            "type": "string",
                            "description": "[CREATION required, UPDATE optional] User ID of the program owner."
                        },
                        "description": {
                            "type": "string",
                            "description": "[CREATION optional, UPDATE optional] Program description."
                        },
                        "status": {
                            "type": "string",
                            "description": "[CREATION optional, UPDATE optional] Program status.",
                            "enum": ["open", "in_progress", "blocked", "closed"]
                        }
                    },
                    "required": [],
                    "oneOf": [
                        {
                            "required": ["program_id"]
                        },
                        {
                            "required": ["program_key"]
                        },
                        {
                            "required": ["program_key", "program_name", "program_owner_user_id"]
                        }
                    ]
                }
            }
        }
