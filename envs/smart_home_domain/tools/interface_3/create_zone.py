import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class CreateZone(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        zone_name: str,
        zone_type: str,
    ) -> str:
        """Create a new zone under an existing household."""
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

            if zone_name is None or not isinstance(zone_name, str) or not zone_name.strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": "zone_name is required. Provide the descriptive name of the area to create.",
                    }
                )

            allowed_zone_types = {
                "bedroom",
                "kitchen",
                "lounge",
                "bathroom",
                "living_room",
                "dining_room",
                "garage",
                "hallway",
                "storage",
                "office",
                "custom",
            }
            timestamp = "2025-12-19T23:59:00"

            home_name_clean = home_name.strip()
            zone_name_clean = zone_name.strip()

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

            if zone_type is None or not isinstance(zone_type, str) or not zone_type.strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": "zone_type is required and must match the zone enum.",
                    }
                )

            zone_type_clean = zone_type.strip().lower()
            if zone_type_clean not in allowed_zone_types:
                return json.dumps(
                    {
                        "success": False,
                        "error": "zone_type must match the zone enum values: bedroom, kitchen, lounge, bathroom, living_room, dining_room, garage, hallway, storage, office, custom.",
                    }
                )
            final_zone_type = zone_type_clean

            for record in rooms.values():
                if str(record.get("home_id", "")).strip() != home_id_str:
                    continue
                existing_name = str(record.get("room_name", "")).strip()
                if existing_name.lower() == zone_name_clean.lower():
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"A zone named '{zone_name_clean}' already exists in this household.",
                        }
                    )

            numeric_ids = []
            for key in rooms.keys():
                try:
                    numeric_ids.append(int(str(key)))
                except ValueError:
                    continue
            next_id = max(numeric_ids) + 1 if numeric_ids else len(rooms) + 1
            new_zone_id = str(next_id)

            new_room = {
                "room_id": new_zone_id,
                "home_id": home_id_str,
                "room_name": zone_name_clean,
                "room_type": final_zone_type,
                "created_at": timestamp,
                "updated_at": timestamp,
            }
            rooms[new_zone_id] = new_room

            return json.dumps(
                {
                    "success": True,
                    "zone": {
                        "zone_id": new_zone_id,
                        "zone_name": zone_name_clean,
                        "zone_type": final_zone_type,
                        "home_id": home_id_str,
                        "home_name": matched_home.get("home_name"),
                        "created_at": timestamp,
                        "updated_at": timestamp,
                    },
                }
            )
        except Exception as exc:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Failed to create zone: {exc}",
                }
            )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_zone",
                "description": (
                    "Create a new household zone (room) within a home so devices can be organized by location. "
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the household where the zone will be created. Used to validate the home exists.",
                        },
                        "zone_name": {
                            "type": "string",
                            "description": "Required descriptive name of the zone to create. Must be unique within the household.",
                        },
                        "zone_type": {
                            "type": "string",
                            "description": "Required zone classification such as bedroom, kitchen, lounge, bathroom, living_room, dining_room, garage, hallway, storage, office, or custom.",
                        },
                    },
                    "required": ["home_name", "zone_name", "zone_type"],
                },
            },
        }
