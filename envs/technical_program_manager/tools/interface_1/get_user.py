import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class GetUser(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], user_id: Optional[str] = None, email: Optional[str] = None) -> str:
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for users"
            })
        
        users = data.get("users", {})
        
        if not user_id and not email:
            return json.dumps({
                "success": False,
                "error": "At least one parameter (user_id or email) must be provided"
            })
        
        found_user = None
        found_id = None
        
        if user_id:
            if str(user_id) in users:
                found_user = users[str(user_id)]
                found_id = str(user_id)
            else:
                return json.dumps({
                    "success": False,
                    "error": f"User with ID '{user_id}' not found"
                })
        
        elif email:
            for uid, user_info in users.items():
                if user_info.get("email") == email:
                    found_user = user_info
                    found_id = str(uid)
                    break
            
            if not found_user:
                return json.dumps({
                    "success": False,
                    "error": f"User with email '{email}' not found"
                })
        
        user_data = {
            "user_id": str(found_id),
            "username": str(found_user.get("username", "")),
            "email": str(found_user.get("email", "")),
            "first_name": str(found_user.get("first_name", "")) if found_user.get("first_name") is not None else None,
            "last_name": str(found_user.get("last_name", "")) if found_user.get("last_name") is not None else None,
            "role": str(found_user.get("role", "")),
            "status": str(found_user.get("status", "")),
            "created_at": str(found_user.get("created_at", "")) if found_user.get("created_at") is not None else None,
            "updated_at": str(found_user.get("updated_at", "")) if found_user.get("updated_at") is not None else None
        }
        
        return json.dumps({
            "success": True,
            "user_data": user_data
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_user",
                "description": "Retrieves user information from the system. Use this to authenticate users, verify user roles and permissions, get user details for assignments, or look up contact information for stakeholder communication.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The unique identifier of the user"
                        },
                        "email": {
                            "type": "string",
                            "description": "The email address of the user"
                        }
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["email"]},
                        {"required": ["user_id"]}
                    ]  
                }
            }
        }
