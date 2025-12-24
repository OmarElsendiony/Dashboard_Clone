import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool

class RetrieveHouseholdZones(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: str,
        zone_name: Optional[str] = None,
        home_name: Optional[str] = None,
        zone_type: Optional[str] = None,
    ) -> str:
        try:
            if not isinstance(data, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Invalid payload: data must be a dictionary representing the state.",
                    }
                )

            homes = data.get("homes")
            rooms = data.get("rooms")

            if not isinstance(homes, dict) or not isinstance(rooms, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Missing homes or rooms collections in the dataset.",
                    }
                )

            if home_id is None or str(home_id).strip() == "":
                return json.dumps(
                    {
                        "success": False,
                        "error": "home_id is required and cannot be empty.",
                    }
                )

            normalized_home_id = str(home_id).strip() if home_id else None
            normalized_home_name = (
                home_name.strip().lower() if isinstance(home_name, str) else None
            )

            matched_home = None
            for record in homes.values():
                record_id = str(record.get("home_id", "")).strip()
                record_name = str(record.get("home_name", "")).strip()
                if normalized_home_id and record_id == normalized_home_id:
                    matched_home = record
                    break
                if normalized_home_name and record_name.lower() == normalized_home_name:
                    matched_home = record
                    break

            if matched_home is None:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Household not found using the provided identifiers.",
                    }
                )

            if (
                normalized_home_name
                and str(matched_home.get("home_name", "")).strip().lower()
                != normalized_home_name
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": "The provided home_name does not match the located household record.",
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

            normalized_zone_name = None
            if isinstance(zone_name, str) and zone_name.strip():
                normalized_zone_name = zone_name.strip().lower()
            normalized_zone_type = None
            if zone_type is not None:
                if not isinstance(zone_type, str):
                    return json.dumps(
                        {
                            "success": False,
                            "error": "zone_type must be a string that matches the zone enum.",
                        }
                    )
                candidate = zone_type.strip().lower()
                if candidate not in allowed_zone_types:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "zone_type must match the rooms enum values: bedroom, kitchen, lounge, bathroom, living_room, dining_room, garage, hallway, storage, office, custom.",
                        }
                    )
                normalized_zone_type = candidate

            matched_rooms: List[Dict[str, Any]] = []
            for record in rooms.values():
                record_home_id = str(record.get("home_id", "")).strip()
                if record_home_id != str(matched_home.get("home_id", "")).strip():
                    continue

                record_name = str(record.get("room_name", "")).strip()
                record_type = str(record.get("room_type", "")).strip().lower()

                if normalized_zone_name and normalized_zone_name not in record_name.lower():
                    continue

                if normalized_zone_type and record_type != normalized_zone_type:
                    continue

                matched_rooms.append(record)

            if not matched_rooms:
                return json.dumps(
                    {
                        "success": False,
                        "error": "No zones match the provided filters for this household.",
                    }
                )

            updated_entries: List[Dict[str, Any]] = []
            for record in matched_rooms:
                zone_payload = {
                    "zone_id": record.get("room_id"),
                    "zone_name": record.get("room_name"),
                    "zone_type": record.get("room_type"),
                    "home_id": record.get("home_id"),
                    "home_name": matched_home.get("home_name"),
                    "created_at": record.get("created_at"),
                    "updated_at": record.get("updated_at"),
                }
                updated_entries.append(zone_payload)

            return json.dumps(
                {
                    "success": True,
                    "home": {
                        "home_id": matched_home.get("home_id"),
                        "home_name": matched_home.get("home_name"),
                    },
                    "zones": updated_entries,
                }
            )
        except Exception as exc:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Failed to retrieve household zones: {exc}",
                }
            )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "retrieve_household_zones",
                "description": (
                    "Review the zones belonging to a household."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "Unique household identifier. Required and must not be empty.",
                        },
                        "home_name": {
                            "type": "string",
                            "description": "Household name; defaults to using home_id when omitted.",
                        },
                        "zone_name": {
                            "type": "string",
                            "description": "Optional zone name. When omitted, returns all zones.",
                        },
                        "zone_type": {
                            "type": "string",
                            "description": "Filter for the current zone classification (bedroom, kitchen, lounge, bathroom, living_room, dining_room, garage, hallway, storage, office, or custom). Defaults to no type filtering when omitted.",
                        },
                    },
                    "required": ["home_id"],
                },
            },
        }
