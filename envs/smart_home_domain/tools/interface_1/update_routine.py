import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdateRoutine(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        new_routine_data: Dict[str, Any],
        routine_id: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        
        routines = data.get("routines", {})
        if routine_id:
            routine = routines.get(routine_id)
        else:
            return json.dumps({"success": False, "error": "No routine specified"})
        if not routine:
            return json.dumps({"success": False, "error": "Routine not found"})
        if not new_routine_data:
            return json.dumps(
                {"success": False, "error": "No new routine data provided"}
            )
            
        # Update the routine with new data
        updated_routine = (
            {**routine, **new_routine_data, "updated_at": "2025-12-19T23:59:00"}
            if new_routine_data
            else routine
        )
        routines[routine_id] = updated_routine
        data["routines"] = routines
        
        return json.dumps({"success": True, "routine": routines[routine_id]})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_routine",
                "description": "Update the details of a routine.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "routine_id": {
                            "type": "string",
                            "description": "The ID of the routine to be updated.",
                        },
                        "new_routine_data": {
                            "type": "object",
                            "description": "A dictionary containing the new data for the routine. Including routine_name and description.",
                        },
                    },
                    "required": ["routine_id", "new_routine_data"],
                },
            },
        }
