import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class EnableRoutine(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], routine_id: str) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        # Implement your tool logic here
        routines = data.get("routines", {})
        if routine_id:
            routine = routines.get(routine_id)
        else:
            return json.dumps({"success": False, "error": "No routine specified"})
        if not routine:
            return json.dumps({"success": False, "error": "Routine not found"})
        # Update the enabled status of the routine
        routines[routine_id] = {
            **routine,
            "status": "enabled",
            "updated_at": "2025-12-19T23:59:00",
        }
        data["routines"] = routines
        return json.dumps({"success": True, "routine": routines[routine_id]})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "enable_routine",
                "description": "Update the status of a routine to enabled.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "routine_id": {
                            "type": "string",
                            "description": "The ID of the routine to be enabled.",
                        },
                    },
                    "required": ["routine_id"],
                },
            },
        }
