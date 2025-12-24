import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class ListAutomations(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        status: Optional[str] = None,
    ) -> str:
        """
        List routines in a home, optionally filtered by status.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        routines = data.get("routines")

        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})
        if not isinstance(routines, dict):
            return json.dumps({"success": False, "error": "routines store missing"})

        if not isinstance(home_name, str) or not home_name.strip():
            return json.dumps({"success": False, "error": "home_name must be provided"})
        home_name = home_name.strip()

        # Find home by name
        home_id = None
        for hid, home in homes.items():
            if home.get("home_name", "").strip().lower() == home_name.lower():
                home_id = hid
                break
        if not home_id:
            return json.dumps({"success": False, "error": f"Home '{home_name}' not found"})

        status_filter = None
        if status:
            if not isinstance(status, str):
                return json.dumps({"success": False, "error": "status must be a string"})
            status_filter = status.strip().lower()
            if status_filter not in {"enabled", "disabled"}:
                return json.dumps({"success": False, "error": "status must be one of enabled, disabled"})

        result_automations = []
        for routine in routines.values():
            if routine.get("home_id") == home_id:
                if status_filter and routine.get("status") != status_filter:
                    continue
                # Return SOP terminology only (do not leak DB field names)
                result_automations.append({
                    "automation_id": routine.get("routine_id"),
                    "automation_name": routine.get("routine_name"),
                    "status": routine.get("status"),
                    "description": routine.get("description"),
                    "created_at": routine.get("created_at"),
                    "updated_at": routine.get("updated_at"),
                })

        return json.dumps({"success": True, "automations": result_automations})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_automations",
                "description": "List all automation routines in a home, optionally filtered by status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional status filter; allowed values: enabled, disabled.",
                        },
                    },
                    "required": ["home_name"],
                },
            },
        }

