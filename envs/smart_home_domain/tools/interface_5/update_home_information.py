import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpdateHomeInformation(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        new_home_name: Optional[str] = None,
        guest_mode_enabled: Optional[bool] = None,
    ) -> str:
        """
        Update home details.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")

        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})

        if not isinstance(home_name, str) or not home_name.strip():
            return json.dumps({"success": False, "error": "home_name must be provided"})
        home_name = home_name.strip()

        # Find home by name
        home_id = None
        home = None
        for hid, h in homes.items():
            if h.get("home_name", "").strip().lower() == home_name.lower():
                home_id = hid
                home = h
                break
        
        if not home_id:
            return json.dumps({"success": False, "error": f"Home '{home_name}' not found"})

        updates = False

        if new_home_name is not None:
            if not isinstance(new_home_name, str) or not new_home_name.strip():
                return json.dumps({"success": False, "error": "new_home_name must be a non-empty string"})
            new_name = new_home_name.strip()
            
            # Check if new home name is unique across database
            for hid, h in homes.items():
                if hid != home_id and h.get("home_name", "").strip().lower() == new_name.lower():
                    return json.dumps({"success": False, "error": f"Home name '{new_name}' already exists"})
            
            home["home_name"] = new_name
            updates = True

        if guest_mode_enabled is not None:
            home["guest_mode_enabled"] = bool(guest_mode_enabled)
            updates = True

        if not updates:
            return json.dumps({"success": False, "error": "No updates provided"})

        home["updated_at"] = "2025-12-19T23:59:00"

        return json.dumps({"success": True, "home": home})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_home_information",
                "description": "Update home information including name and guest mode.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Current name of the home to update.",
                        },
                        "new_home_name": {
                            "type": "string",
                            "description": "Optional new name for the home; must be unique across all homes.",
                        },
                        "guest_mode_enabled": {
                            "type": "boolean",
                            "description": "Optional guest mode setting (True/False).",
                        },
                    },
                    "required": ["home_name"],
                },
            },
        }

