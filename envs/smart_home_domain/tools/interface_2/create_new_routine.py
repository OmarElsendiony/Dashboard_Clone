import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateNewRoutine(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: str,
        created_by_user_id: str,
        routine_name: str,
        description: Optional[str] = None
    ) -> str:
        """
        Create a new routine in the smart home system.
        
        Args:
            data: The data dictionary containing all smart home data.
            home_id: The home ID where the routine will be created (required).
            created_by_user_id: The user ID who creates the routine (required).
            routine_name: The name of the routine (required).
            description: Description of the routine (optional, defaults to empty string).
            
        Returns:
            JSON string containing the success status and the newly created routine.
        """
        routines = data.setdefault("routines", {})
        homes = data.get("homes", {})
        users = data.get("users", {})
        
        # Validate that the home exists
        if str(home_id) not in homes:
            return json.dumps({
                "success": False,
                "error": f"Home ID {home_id} not found"
            })
        
        # Validate that the user exists
        if str(created_by_user_id) not in users:
            return json.dumps({
                "success": False,
                "error": f"User ID {created_by_user_id} not found"
            })
        
        # Generate new routine ID
        if routines:
            max_id = max([int(k) for k in routines.keys()])
            new_routine_id = str(max_id + 1)
        else:
            new_routine_id = "1"
        
        # Get current timestamp
        current_timestamp = "2025-12-19T23:59:00"
        
        # Set default description if not provided
        if description is None:
            description = ""
        
        # Create new routine record with status always set to "enabled"
        new_routine = {
            "routine_id": new_routine_id,
            "home_id": str(home_id),
            "created_by_user_id": str(created_by_user_id),
            "routine_name": routine_name,
            "status": "enabled",
            "description": description,
            "created_at": current_timestamp,
            "updated_at": current_timestamp
        }
        
        # Add routine to the routines dictionary
        routines[new_routine_id] = new_routine
        
        return json.dumps({
            "success": True,
            **new_routine
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_new_routine",
                "description": "Create a new routine in the smart home system. The routine status is automatically set to 'enabled'. Validates that both home and user exist before creation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "The home ID where the routine will be created (required)."
                        },
                        "created_by_user_id": {
                            "type": "string",
                            "description": "The user ID who creates the routine (required)."
                        },
                        "routine_name": {
                            "type": "string",
                            "description": "The name of the routine (required)."
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the routine (optional, defaults to empty string)."
                        }
                    },
                    "required": ["home_id", "created_by_user_id", "routine_name"]
                }
            }
        }
