import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdateHome(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: Optional[str] = None,
        home_name: Optional[str] = None,
        target_info: Optional[Dict[str, Any]] = None,
        new_address: Optional[Dict[str, Any]] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        homes = data.get("homes", {})
        addresses = data.get("addresses", {})
        address = new_address
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
        target_address_id = home.get("address_id")
        if not home:
            return json.dumps({"success": False, "error": "Home not found"})
        if not address and not target_info:
            return json.dumps(
                {"success": False, "error": "No update information provided"}
            )
        if address:
            try:
                if target_address_id and target_address_id in addresses:
                    addresses[target_address_id].update(address)
            except Exception as e:
                return json.dumps(
                    {"success": False, "error": f"Failed to update address: {str(e)}"}
                )
        if target_info:
            try:
                home.update(target_info)
            except Exception as e:
                return json.dumps(
                    {"success": False, "error": f"Failed to update home info: {str(e)}"}
                )
        return json.dumps(
            {"success": True, "home": home, "address": addresses[target_address_id]}
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_home",
                "description": "Update the information of a smart home and its address. You can update home_name, and address details such as street, city, country, and house_number.",
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
                        "target_info": {
                            "type": "object",
                            "description": "The information to update in the home. Options include home_name etc. E.g. {'home_name': 'New Home Name'}.",
                        },
                        "new_address": {
                            "type": "object",
                            "description": "The new address information for the home. Options include street, city, country, house_number.",
                        },
                    },
                    "required": [],
                },
            },
        }
