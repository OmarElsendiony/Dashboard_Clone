import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class GetProgram(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        program_id: Optional[str] = None,
        program_name: Optional[str] = None,
        program_key: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for projects"
            })
        
        projects = data.get("projects", {})
        
        if not program_id and not program_name and not program_key:
            return json.dumps({
                "success": False,
                "error": "At least one parameter (program_id, program_name, or program_key) must be provided"
            })
        
        found_project = None
        found_id = None
        
        if program_id:
            if str(program_id) in projects:
                found_project = projects[str(program_id)]
                found_id = str(program_id)
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Program with ID '{program_id}' not found"
                })
        
        elif program_name:
            for pid, project_info in projects.items():
                if project_info.get("project_name") == program_name or \
                   project_info.get("program_name") == program_name:
                    found_project = project_info
                    found_id = str(pid)
                    break
            
            if not found_project:
                return json.dumps({
                    "success": False,
                    "error": f"Program with name '{program_name}' not found"
                })
        
        elif program_key:
            for pid, project_info in projects.items():
                if project_info.get("project_key") == program_key or \
                   project_info.get("program_key") == program_key:
                    found_project = project_info
                    found_id = str(pid)
                    break
            
            if not found_project:
                return json.dumps({
                    "success": False,
                    "error": f"Program with key '{program_key}' not found"
                })
        
        program_data = {}
        program_data["program_id"] = found_id
        
        if "project_key" in found_project:
            program_data["program_key"] = found_project["project_key"]
        
        if "project_name" in found_project:
            program_data["program_name"] = found_project["project_name"]
        
        if "project_owner_user_id" in found_project:
            program_data["program_owner_user_id"] = found_project["project_owner_user_id"]
        
        for key, value in found_project.items():
            if key not in ["project_id", "project_key", "project_name", "project_owner_user_id"]:
                program_data[key] = value
        
        return json.dumps({
            "success": True,
            "program_data": program_data
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_program",
                "description": "Retrieves program information. Use this to check program status, get program details for reporting, verify program existence before operations, or retrieve program scope and ownership information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "program_id": {
                            "type": "string",
                            "description": "The unique identifier of the program"
                        },
                        "program_name": {
                            "type": "string",
                            "description": "The name of the program"
                        },
                        "program_key": {
                            "type": "string",
                            "description": "The unique key of the program"
                        }
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["program_id"]},
                        {"required": ["program_name"]},
                        {"required": ["program_key"]}
                    ]
                }
            }
        }
