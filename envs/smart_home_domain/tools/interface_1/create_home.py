import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class CreateHome(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any], home_name: str, address: Dict[str, Any], user_id: str
    ) -> str:

        def generate_id(table: Dict[str, Any]) -> int:
            return max([int(k) for k in table.keys()], default=0) + 1

        timestamp = "2025-12-19T23:59:00"
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        homes = data.get("homes", {})
        addresses = data.get("addresses", {})
        users = data.get("users", {})
        home_users = data.get("home_users", {})

        if user_id not in users:
            return json.dumps({"success": False, "error": "user ID does not exist"})

        home_id = generate_id(homes)
        address_id = generate_id(addresses)

        address = json.loads(json.dumps(address))  # Ensure address is a dict
        if not home_name or not address or not user_id:
            return json.dumps({"success": False, "error": "Missing required fields"})

        if not isinstance(address, dict):
            return json.dumps({"success": False, "error": "Invalid address format"})

        street = address.get("street", "")
        city = address.get("city", "")
        country = address.get("country", "")
        house_number = address.get("house_number", "")
        if not street or not city or not country or not house_number:
            return json.dumps(
                {"success": False, "error": "Incomplete address information"}
            )
        new_address = {
            "address_id": str(address_id),
            "street": street,
            "city": city,
            "country": country,
            "house_number": house_number,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        addresses[str(address_id)] = new_address
        new_home = {
            "home_id": str(home_id),
            "home_name": home_name,
            "address_id": str(address_id),
            "owner_id": user_id,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        homes[str(home_id)] = new_home
        home_user_id = generate_id(home_users)
        new_home_user = {
            "home_user_id": str(home_user_id),
            "home_id": str(home_id),
            "user_id": user_id,
            "role": "admin",
            "access_expires_at": None,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        home_users[str(home_user_id)] = new_home_user
        data["homes"] = homes
        data["addresses"] = addresses
        data["home_users"] = home_users
        return json.dumps({"success": True, "home": new_home, "address": new_address})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_home",
                "description": "Create a new home for the give user_id.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "The name of the home to be created.",
                        },
                        "address": {
                            "type": "object",
                            "description": "The address object of the home to be created. Includes street, city, country, and house_number.",
                            "properties": {
                                "street": {
                                    "type": "string",
                                    "description": "The street of the address.",
                                },
                                "city": {
                                    "type": "string",
                                    "description": "The city of the address.",
                                },
                                "country": {
                                    "type": "string",
                                    "description": "The country of the address.",
                                },
                                "house_number": {
                                    "type": "string",
                                    "description": "The house number of the address.",
                                },
                            },
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user creating the home.",
                        },
                    },
                    "required": ["home_name", "address", "user_id"],
                },
            },
        }
