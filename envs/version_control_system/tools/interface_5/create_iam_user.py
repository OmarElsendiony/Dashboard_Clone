import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateIamUser(Tool):
    
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        email: str,
        username: str,
        full_name: Optional[str] = None,
    ) -> str:
      

        def generate_id(table: Dict[str, Any]) -> str:
          
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        users = data.get("users", {})

        # Validate required fields
        if not email:
            return json.dumps({"success": False, "error": "Missing required parameter: email"})

        if not username:
            return json.dumps({"success": False, "error": "Missing required parameter: username"})

        # Check if email already exists
        for _, user in users.items():
            if user.get("email") == email:
                return json.dumps({
                    "success": False,
                    "error": f"User with email '{email}' already exists"
                })

        # Check if username already exists
        for _, user in users.items():
            if user.get("username") == username:
                return json.dumps({
                    "success": False,
                    "error": f"User with username '{username}' already exists"
                })

        # Generate new user ID
        new_user_id = generate_id(users)

        # Set timestamp for created_at and updated_at
        timestamp = "2026-01-01T23:59:00"

        # Create new user record with default values
        new_user = {
            "user_id": new_user_id,
            "username": username,
            "email": email,
            "full_name": full_name if full_name else "",
            "bio": "",
            "account_type": "personal",
            "plan_type": "free",
            "status": "active",
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        # Add the new user to the users dictionary
        users[new_user_id] = new_user

        # Return user data without internal fields (plan_type, account_type)
        returned_user_data = {
            "user_id": new_user_id,
            "username": username,
            "email": email,
            "full_name": full_name if full_name else "",
            "bio": "",
            "status": "active",
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        return json.dumps({
            "success": True,
            "message": f"User '{username}' created successfully",
            "user_data": returned_user_data
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_iam_user",
                "description": "Creates a new IAM user in the version control system.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "The email address of the new user. Required field and must be unique across all users.",
                        },
                        "username": {
                            "type": "string",
                            "description": "The username for the new user. Required field and must be unique across all users.",
                        },
                        "full_name": {
                            "type": "string",
                            "description": "The full name of the user. Optional field.",
                        },
                    },
                    "required": ["email", "username"],
                },
            },
        }
