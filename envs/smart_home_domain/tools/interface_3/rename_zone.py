import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class RenameZone(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        current_zone_name: str,
        new_zone_name: str,
    ) -> str:
        """Rename or reclassify an existing household zone."""
        try:
            if not isinstance(data, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Invalid payload: data must be the state dictionary.",
                    }
                )

            homes = data.get("homes")
            rooms = data.get("rooms")

            if not isinstance(homes, dict) or not isinstance(rooms, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Missing homes or zones collections in the dataset.",
                    }
                )

            if home_name is None or not isinstance(home_name, str) or not home_name.strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": "home_name is required so the household can be validated.",
                    }
                )

            if current_zone_name is None or not isinstance(current_zone_name, str) or not current_zone_name.strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": "current_zone_name is required to locate the zone that needs updates.",
                    }
                )

            if new_zone_name is None or not isinstance(new_zone_name, str) or not new_zone_name.strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": "new_zone_name is required. Provide the updated descriptive label for the area.",
                    }
                )

            timestamp = "2025-12-19T23:59:00"

            home_name_clean = home_name.strip()
            current_zone_name_clean = current_zone_name.strip().lower()
            new_zone_name_clean = new_zone_name.strip()

            matches = [
                record
                for record in homes.values()
                if isinstance(record, dict)
                and str(record.get("home_name", "")).strip().lower()
                == home_name_clean.lower()
            ]

            if not matches:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Household not found.",
                    }
                )


            matched_home = matches[0]
            home_id_str = str(matched_home.get("home_id", "")).strip()

            zone_matches = [
                record
                for record in rooms.values()
                if str(record.get("home_id", "")).strip() == home_id_str
                and str(record.get("room_name", "")).strip().lower() == current_zone_name_clean
            ]

            if not zone_matches:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Zone not found for this household. Confirm the current zone name from retrieve_household_zones.",
                    }
                )


            target_zone = zone_matches[0]
            zone_id = str(target_zone.get("room_id", "")).strip()

            for record in rooms.values():
                if str(record.get("home_id", "")).strip() != home_id_str:
                    continue
                if str(record.get("room_id", "")).strip() == zone_id:
                    continue
                record_name = str(record.get("room_name", "")).strip()
                if record_name.lower() == new_zone_name_clean.lower():
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"A zone named '{new_zone_name_clean}' already exists in this household.",
                        }
                    )

            previous_zone_name = target_zone.get("room_name")

            target_zone["room_name"] = new_zone_name_clean
            target_zone["updated_at"] = timestamp

            return json.dumps(
                {
                    "success": True,
                    "message": f"Zone '{previous_zone_name}' renamed to '{new_zone_name_clean}'.",
                    "home": {
                        "home_id": home_id_str,
                        "home_name": matched_home.get("home_name"),
                    },
                    "zone": {
                        "zone_id": zone_id,
                        "zone_name": target_zone.get("room_name"),
                        "zone_type": target_zone.get("room_type"),
                        "updated_at": target_zone.get("updated_at"),
                    }
                }
            )
        except Exception as exc:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Failed to rename zone: {exc}",
                }
            )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
                    "function": {
                "name": "rename_zone",
                "description": (
                    "Rename an existing zone (room) within a household."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Required name of the household where the zone exists.",
                        },
                        "current_zone_name": {
                            "type": "string",
                            "description": "Required existing zone name as currently configured.",
                        },
                        "new_zone_name": {
                            "type": "string",
                            "description": "Required new descriptive name for the zone. Must be unique within the household.",
                        },
                    },
                    "required": ["home_name", "current_zone_name", "new_zone_name"],
                },
            },
        }
