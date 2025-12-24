import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class GetRoutine(Tool):
    @staticmethod
    def invoke(
    data: Dict[str, Any],
    routine_name: str,
    home_id: str,
    ) -> str:
        """
        Get routine information by routine name and home ID.
        """
        routines = data.get("routines", {})

        # Search for routine by name and home_id
        matching_routines = []
        for routine_id, routine_data in routines.items():
            if (routine_data.get("routine_name") == routine_name and 
                routine_data.get("home_id") == home_id):
                matching_routines.append({
                    "routine_id": routine_id,
                    **routine_data
                })

        if not matching_routines:
            return json.dumps({
                "success": False,
                "error": f"Routine with name '{routine_name}' not found in home '{home_id}'"
            })

        # Return the first matching routine (should be unique due to schema constraint)
        return json.dumps({
            "success": True,
            "routine_data": matching_routines[0]
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_routine",
                "description": "Retrieve routine information by routine name and home ID. Returns the routine details including routine_id, status, description, and other metadata.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "routine_name": {
                            "type": "string",
                            "description": "The name of the routine to retrieve"
                        },
                        "home_id": {
                            "type": "string",
                            "description": "The ID of the home where the routine is located"
                        }
                    },
                    "required": ["routine_name", "home_id"]
                }
            }
        }
