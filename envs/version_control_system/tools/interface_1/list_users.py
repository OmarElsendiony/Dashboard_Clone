import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ListUsers(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        username: Optional[str] = None,
        user_id: Optional[str] = None,
        account_type: Optional[str] = None
    ) -> str:
        """
        List users filtered by username, user_id, or account_type.
        """
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for users"
            })
        
        users = data.get("users", {})
        results = []
        
        for uid, user_data in users.items():
            # Apply filters
            if username and user_data.get("username") != username:
                continue
            if user_id and uid != user_id:
                continue
            if account_type and user_data.get("account_type") != account_type:
                continue
            
            # Remove plan_type from output if it exists
            filtered_data = {k: v for k, v in user_data.items() if k != "plan_type"}
            
            results.append({**filtered_data, "user_id": uid})
        
        return json.dumps({
            "success": True,
            "count": len(results),
            "results": results
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_users",
                "description": "List users. Can filter by username, user_id, or account_type. Returns all users if no filters are provided.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "Filter by username (exact match)"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "Filter by user_id (exact match)"
                        },
                        "account_type": {
                            "type": "string",
                            "description": "Filter by account type. Allowed values: 'personal', 'organization'"
                        }
                    },
                    "required": []
                }
            }
        }