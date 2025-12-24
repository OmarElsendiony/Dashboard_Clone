import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class InspectHousehold(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        home_id: str = None,
        owner_id: str = None,
    ) -> str:
        """
        Return only the household record identified by home_name (optionally narrowed by home_id and owner_id).
        """
        try:
            if not isinstance(data, dict):
                return json.dumps({"success": False, "error": "Smart Home dataset must be a dictionary."})

            homes = data.get("homes")
            if not isinstance(homes, dict):
                return json.dumps({"success": False, "error": "homes table missing or invalid."})

            if not isinstance(home_name, str) or not home_name.strip():
                return json.dumps({"success": False, "error": "home_name is required and must be non-empty."})

            home_name_cmp = home_name.strip().lower()
            home_id_cmp = home_id.strip() if isinstance(home_id, str) and home_id.strip() else None
            owner_id_cmp = str(owner_id).strip() if owner_id is not None and str(owner_id).strip() else None

            candidates = []
            for record in homes.values():
                if not isinstance(record, dict):
                    continue
                if record.get("home_name", "").lower() != home_name_cmp:
                    continue
                if home_id_cmp and str(record.get("home_id", "")) != home_id_cmp:
                    continue
                if owner_id_cmp and str(record.get("owner_id", "")) != owner_id_cmp:
                    continue
                candidates.append(record)

            if not candidates:
                return json.dumps({"success": False, "error": "No household matched the provided parameters."})

            household = candidates[0]
            payload = {
                "home_id": household.get("home_id"),
                "home_name": household.get("home_name"),
                "owner_id": household.get("owner_id"),
                "address_id": household.get("address_id"),
                "guest_mode_enabled": household.get("guest_mode_enabled"),
                "created_at": household.get("created_at"),
                "updated_at": household.get("updated_at"),
            }
            return json.dumps({"success": True, "household": payload})
        except Exception as exc:
            return json.dumps({"success": False, "error": f"inspect_household failed: {exc}"})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "inspect_household",
                "description": (
                    "Inspect a household using home_name (and optionally home_id/owner_id) and return its details."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Required. Household name used for lookup.",
                        },
                        "home_id": {
                            "type": "string",
                            "description": "Optional. Id of the household.",
                        },
                        "owner_id": {
                            "type": "string",
                            "description": "Optional. Filters households to those owned by this owner_id.",
                        },
                    },
                    "required": ["home_name"],
                },
            },
        }
