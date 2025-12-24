import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class ModifyHouseholdProfile(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        attributes_to_update: Dict[str, Any],
        home_id: str = None,
    ) -> str:
        """
        Update fields on an existing household (homes table). The household is located by home_name, with
        optional home_id for disambiguation. attributes_to_update may include new_home_name, new_address_id, and new_owner_id.
        """
        try:
            if not isinstance(data, dict):
                return json.dumps({"success": False, "error": "Smart Home dataset must be a dictionary."})

            homes = data.get("homes")
            addresses = data.get("addresses")
            users = data.get("users")
            home_users = data.get("home_users")
            if not all(isinstance(tbl, dict) for tbl in (homes, addresses, users, home_users)):
                return json.dumps({"success": False, "error": "Required tables missing or invalid."})

            if not isinstance(home_name, str) or not home_name.strip():
                return json.dumps({"success": False, "error": "home_name is required."})

            attributes_to_update = json.loads(attributes_to_update) if isinstance(attributes_to_update, str) else attributes_to_update
            if not isinstance(attributes_to_update, dict) or not attributes_to_update:
                return json.dumps({"success": False, "error": "No updates were provided."})

            target_record = None
            target_home_id = None
            if isinstance(home_id, str) and home_id.strip():
                target_home_id = home_id.strip()
                target_record = homes.get(target_home_id)
            else:
                matches = [
                    (hid, record)
                    for hid, record in homes.items()
                    if isinstance(record, dict)
                    and record.get("home_name", "").lower() == home_name.strip().lower()
                ]
                if matches:
                    target_home_id, target_record = matches[0]

            if not isinstance(target_record, dict):
                return json.dumps({"success": False, "error": "Target household not found."})

            updates = {}

            if "new_home_name" in attributes_to_update:
                new_home_name = attributes_to_update["new_home_name"]
                if not isinstance(new_home_name, str) or not new_home_name.strip():
                    return json.dumps({"success": False, "error": "new_home_name cannot be empty."})
                desired_name_cmp = new_home_name.strip().lower()
                if desired_name_cmp != target_record.get("home_name", "").lower():
                    for hid, record in homes.items():
                        if not isinstance(record, dict):
                            continue
                        if hid == target_home_id:
                            continue
                        if record.get("home_name", "").lower() == desired_name_cmp:
                            return json.dumps({"success": False, "error": "home_name must remain unique across households."})
                    updates["home_name"] = new_home_name.strip()

            if "new_address_id" in attributes_to_update:
                new_address_id = attributes_to_update["new_address_id"]
                if not isinstance(new_address_id, str) or not new_address_id.strip():
                    return json.dumps({"success": False, "error": "new_address_id cannot be empty."})
                address_id_clean = new_address_id.strip()
                if address_id_clean not in addresses:
                    return json.dumps({"success": False, "error": "new_address_id does not reference a known address."})
                updates["address_id"] = address_id_clean

            if "new_owner_id" in attributes_to_update:
                new_owner_id = attributes_to_update["new_owner_id"]
                if not isinstance(new_owner_id, str) or not new_owner_id.strip():
                    return json.dumps({"success": False, "error": "new_owner_id cannot be empty."})
                owner_id_clean = new_owner_id.strip()
                owner_record = users.get(owner_id_clean)
                if not isinstance(owner_record, dict) or owner_record.get("status") != "active":
                    return json.dumps({"success": False, "error": "new_owner_id must reference an active user."})

                household_member = next(
                    (
                        entry
                        for entry in home_users.values()
                        if isinstance(entry, dict)
                        and str(entry.get("home_id")) == target_home_id
                        and str(entry.get("user_id")) == owner_id_clean
                    ),
                    None,
                )
                if household_member is None:
                    return json.dumps({"success": False, "error": "new_owner_id must already belong to the household membership list."})

                updates["owner_id"] = owner_id_clean

            if not updates:
                return json.dumps({"success": False, "error": "No updates were provided."})

            updates["updated_at"] = "2025-12-19T23:59:00"
            target_record.update(updates)

            return json.dumps({"success": True, "household": target_record})
        except Exception as exc:
            return json.dumps({"success": False, "error": f"modify_household_profile failed: {exc}"})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "modify_household_profile",
                "description": (
                    "Update fields on a household (homes table) by supplying home_name (required), "
                    "an attributes_to_update object (new_home_name, new_address_id, new_owner_id), and optional home_id."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Required. Household name used to locate the home.",
                        },
                        "attributes_to_update": {
                            "type": "object",
                            "description": "Required. Object containing optional keys new_home_name, new_address_id, new_owner_id.",
                        },
                        "home_id": {
                            "type": "string",
                            "description": "Optional. Household identifier for identification.",
                        },
                    },
                    "required": ["home_name", "attributes_to_update"],
                },
            },
        }
