import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class DeleteHome(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: Optional[str] = None,
        home_name: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        homes = data.get("homes", {})
        addresses = data.get("addresses", {})
        # Find home_id if home_name is provided
        if home_name and not home_id:
            for h_id, home in homes.items():
                if home.get("home_name") == home_name:
                    home_id = h_id
                    break
            return json.dumps(
                {"success": False, "error": "Home not found"}
            )  # home_name not found
        if not home_id:
            return json.dumps(
                {"success": False, "error": "Home ID or name must be provided"}
            )
        home = homes.get(home_id)  # type: ignore
        if not home:
            return json.dumps({"success": False, "error": "Home not found"})
        target_address_id = home.get("address_id")
        if not home:
            return json.dumps({"success": False, "error": "Home not found"})
        # Delete home and associated address
        try:
            del homes[home_id]
            if target_address_id and target_address_id in addresses:
                del addresses[target_address_id]
        except Exception as e:
            return json.dumps(
                {"success": False, "error": f"Failed to delete home: {str(e)}"}
            )
        return json.dumps(
            {
                "success": True,
                "message": f"Home id {home_id} and associated address id {target_address_id} deleted successfully",
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "delete_home",
                "description": "Delete a smart home and its associated address.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "The unique identifier of the home to be updated.",
                        },
                        "home_name": {
                            "type": "string",
                            "description": "The name of the home to be updated.",
                        },
                    },
                    "required": [],
                },
            },
        }
