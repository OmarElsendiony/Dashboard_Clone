import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetHomeUsers(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: Optional[str] = None,
        home_name: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        home_users = data.get("home_users", {})
        homes = data.get("homes", {})

        # Find home_id if home_name is provided
        if home_name and not home_id:
            for h_id, home in homes.items():
                if home.get("home_name") == home_name:
                    home_id = h_id
                    break

        if not home_id:
            return json.dumps(
                {"success": False, "error": "Home ID or name must be provided"}
            )
        home = homes.get(home_id)
        if not home:
            return json.dumps({"success": False, "error": "Home not found"})
        target_users = [
            home_user
            for home_user in home_users.values()
            if home_user.get("home_id") == home_id
        ]
        return json.dumps({"success": True, "data": target_users})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_home_users",
                "description": "Retrieve the associated users to a home.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "The ID of the home.",
                        },
                        "home_name": {
                            "type": "string",
                            "description": "The name of the home.",
                        },
                    },
                    "required": [],
                },
            },
        }
