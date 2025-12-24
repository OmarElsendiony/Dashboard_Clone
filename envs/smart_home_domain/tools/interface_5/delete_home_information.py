import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class DeleteHomeInformation(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
    ) -> str:
        """
        Delete a home and cascade delete related records.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        home_users = data.get("home_users")
        rooms = data.get("rooms")
        devices = data.get("devices")
        scenes = data.get("scenes")
        routines = data.get("routines")

        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})

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

        deleted_home = homes.pop(home_id)

        if isinstance(home_users, dict):
            to_delete = [k for k, v in home_users.items() if v.get("home_id") == home_id]
            for k in to_delete:
                home_users.pop(k)

        if isinstance(rooms, dict):
            to_delete = [k for k, v in rooms.items() if v.get("home_id") == home_id]
            for k in to_delete:
                rooms.pop(k)

        if isinstance(devices, dict):
            to_delete = [k for k, v in devices.items() if v.get("home_id") == home_id]
            for k in to_delete:
                devices.pop(k)

        if isinstance(scenes, dict):
            to_delete = [k for k, v in scenes.items() if v.get("home_id") == home_id]
            for k in to_delete:
                scenes.pop(k)

        if isinstance(routines, dict):
            to_delete = [k for k, v in routines.items() if v.get("home_id") == home_id]
            for k in to_delete:
                routines.pop(k)

        return json.dumps({"success": True, "deleted_home": deleted_home})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "delete_home_information",
                "description": "Delete a home and all associated data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home to delete.",
                        },
                    },
                    "required": ["home_name"],
                },
            },
        }

