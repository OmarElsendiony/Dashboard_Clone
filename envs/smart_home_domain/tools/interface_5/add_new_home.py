import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class AddNewHome(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        owner_email: str,
        street: str,
        city: str,
        house_number: Optional[str] = None,
        country: Optional[str] = None,
        guest_mode_enabled: Optional[bool] = False,
    ) -> str:
        """
        Create a new home and its address.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(key) for key in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        users = data.get("users")
        addresses = data.get("addresses")
        home_users = data.get("home_users")

        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})
        if not isinstance(users, dict):
            return json.dumps({"success": False, "error": "users store missing"})
        if not isinstance(addresses, dict):
            return json.dumps({"success": False, "error": "addresses store missing"})
        if not isinstance(home_users, dict):
            return json.dumps({"success": False, "error": "home_users store missing"})

        if not isinstance(owner_email, str) or not owner_email.strip():
            return json.dumps({"success": False, "error": "owner_email must be provided"})
        owner_email = owner_email.strip().lower()

        # Find user by email
        owner_id = None
        user = None
        for uid, u in users.items():
            if u.get("email", "").strip().lower() == owner_email:
                owner_id = uid
                user = u
                break
        
        if not owner_id:
            return json.dumps({"success": False, "error": f"User with email '{owner_email}' not found"})

        if user.get("status") != "active":
            return json.dumps({"success": False, "error": f"User with email '{owner_email}' is not active"})

        if not isinstance(home_name, str) or not home_name.strip():
            return json.dumps({"success": False, "error": "home_name must be provided"})
        home_name = home_name.strip()

        # Check if home name already exists
        for home in homes.values():
            if home.get("home_name", "").strip().lower() == home_name.lower():
                return json.dumps({"success": False, "error": f"Home '{home_name}' already exists"})

        if not isinstance(street, str) or not street.strip():
            return json.dumps({"success": False, "error": "street must be provided"})
        street = street.strip()

        if not isinstance(city, str) or not city.strip():
            return json.dumps({"success": False, "error": "city must be provided"})
        city = city.strip()

        # Handle house_number as string or number
        house_num = None
        if house_number is not None:
            if isinstance(house_number, (int, float)):
                house_num = str(int(house_number))
            elif isinstance(house_number, str) and house_number.strip():
                house_num = house_number.strip()
        
        country_val = country.strip() if isinstance(country, str) and country.strip() else None

        guest_mode = bool(guest_mode_enabled)

        timestamp = "2025-12-19T23:59:00"

        address_id = generate_id(addresses)
        address_record = {
            "address_id": address_id,
            "house_number": house_num,
            "street": street,
            "city": city,
            "country": country_val,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        addresses[address_id] = address_record

        home_id = generate_id(homes)
        home_record = {
            "home_id": home_id,
            "owner_id": owner_id,
            "home_name": home_name,
            "address_id": address_id,
            "guest_mode_enabled": guest_mode,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        homes[home_id] = home_record

        # Automatically add owner as admin
        home_user_id = generate_id(home_users)
        home_user_record = {
            "home_user_id": home_user_id,
            "home_id": home_id,
            "user_id": owner_id,
            "role": "admin",
            "access_expires_at": None,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        home_users[home_user_id] = home_user_record

        return json.dumps({
            "success": True,
            "home": {
                "home_name": home_record.get("home_name"),
                "owner_email": owner_email,
                "guest_mode_enabled": home_record.get("guest_mode_enabled"),
                "created_at": home_record.get("created_at"),
                "updated_at": home_record.get("updated_at"),
            },
            "address": {
                "house_number": address_record.get("house_number"),
                "street": address_record.get("street"),
                "city": address_record.get("city"),
                "country": address_record.get("country"),
                "created_at": address_record.get("created_at"),
                "updated_at": address_record.get("updated_at"),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_new_home",
                "description": "Create a new home with address information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home; must be unique across all homes in the system. This will be used to identify the home in future operations.",
                        },
                        "owner_email": {
                            "type": "string",
                            "description": "Email address of the user who will own the home. The user must exist in the system and have an active status. The owner will automatically be assigned the admin role for this home.",
                        },
                        "street": {
                            "type": "string",
                            "description": "Street name for the home's physical address (e.g., 'Main Street', 'Oak Avenue').",
                        },
                        "city": {
                            "type": "string",
                            "description": "City name where the home is located (e.g., 'San Francisco', 'New York').",
                        },
                        "house_number": {
                            "type": ["string", "number"],
                            "description": "house or building number for the home's address. Can be a number (e.g., 123, 34) or string (e.g., '45B', 'Apt 5C').",
                        },
                        "country": {
                            "type": "string",
                            "description": "Country name where the home is located (e.g., 'United States', 'Canada', 'United Kingdom').",
                        },
                        "guest_mode_enabled": {
                            "type": "boolean",
                            "description": "Whether guest mode is enabled for this home (True/False). When enabled, allows temporary guest access to the home. Defaults to False if not specified.",
                        },
                    },
                    "required": ["home_name", "owner_email", "street", "city"],
                },
            },
        }

