import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class EstablishHousehold(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        owner_id: str,
        address_id: str,
    ) -> str:
        """
        Insert a new household row in the homes table using the provided basic metadata.
        """
        try:
            if not isinstance(data, dict):
                return json.dumps({"success": False, "error": "Smart Home dataset must be a dictionary."})

            homes = data.get("homes")
            addresses = data.get("addresses")
            users = data.get("users")
            if not isinstance(homes, dict):
                return json.dumps({"success": False, "error": "homes table missing or invalid."})
            if not isinstance(addresses, dict):
                return json.dumps({"success": False, "error": "addresses table missing or invalid."})
            if not isinstance(users, dict):
                return json.dumps({"success": False, "error": "users table missing or invalid."})

            if not isinstance(home_name, str) or not home_name.strip():
                return json.dumps({"success": False, "error": "home_name is required."})

            if not isinstance(owner_id, str) or not owner_id.strip():
                return json.dumps({"success": False, "error": "owner_id is required."})

            numeric_ids = []
            for key in homes.keys():
                try:
                    numeric_ids.append(int(key))
                except (TypeError, ValueError):
                    continue
            new_home_id = str(max(numeric_ids, default=0) + 1)

            home_name_cmp = home_name.strip().lower()
            for existing in homes.values():
                if not isinstance(existing, dict):
                    continue
                if existing.get("home_name", "").lower() == home_name_cmp:
                    return json.dumps({"success": False, "error": "home_name must be unique."})

            owner_id_str = owner_id.strip()
            if owner_id_str not in users:
                return json.dumps({"success": False, "error": "owner_id does not reference a known user."})

            address_id_clean = None
            if isinstance(address_id, str) and address_id.strip():
                address_id_clean = address_id.strip()
                if address_id_clean not in addresses:
                    return json.dumps({"success": False, "error": "address_id does not reference a known address."})

            record = {
                "home_id": new_home_id,
                "home_name": home_name.strip(),
                "owner_id": owner_id_str,
                "address_id": address_id_clean,
                "guest_mode_enabled": False,
                "created_at": "2025-12-19T23:59:00",
                "updated_at": "2025-12-19T23:59:00",
            }
            homes[new_home_id] = record

            return json.dumps({"success": True, "household": record})
        except Exception as exc:
            return json.dumps({"success": False, "error": f"establish_household failed: {exc}"})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "establish_household",
                "description": (
                    "Create a new household (homes table entry) by providing home details."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Required. Name assigned to the new household.",
                        },
                        "owner_id": {
                            "type": "string",
                            "description": "Required. Owner user identifier for the household.",
                        },
                        "address_id": {
                            "type": "string",
                            "description": "Required. Address identifier associated with the household.",
                        },
                    },
                    "required": ["home_name", "owner_id", "address_id"],
                },
            },
        }
