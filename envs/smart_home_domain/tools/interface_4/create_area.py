import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class CreateArea(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        area_name: str,
        area_type: str,
        household_id: str,
    ) -> str:
        timestamp = "2025-12-19T23:59:00"

        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        rooms_dict = data.get("rooms", {})
        if not isinstance(rooms_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid rooms container: expected dict at data['rooms']",
                }
            )

        homes_dict = data.get("homes", {})
        if not isinstance(homes_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid homes container: expected dict at data['homes']",
                }
            )

        # Validate required parameters
        if not area_name:
            return json.dumps({"success": False, "error": "area_name is required"})

        if not area_type:
            return json.dumps({"success": False, "error": "area_type is required"})

        if not household_id:
            return json.dumps({"success": False, "error": "household_id is required"})

        # Convert to strings for consistent comparison
        area_name_str = str(area_name).strip()
        area_type_str = str(area_type).strip()
        household_id_str = str(household_id).strip()

        # Validate household exists
        if household_id_str not in homes_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Household with ID '{household_id_str}' not found",
                }
            )

        home_info = homes_dict[household_id_str]
        if not isinstance(home_info, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid household data for ID '{household_id_str}'",
                }
            )

        # Validate area_type
        valid_area_types = [
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
        ]
        if area_type_str not in valid_area_types:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid area_type '{area_type_str}'. Must be one of: {', '.join(valid_area_types)}",
                }
            )

        # Check if area_name already exists in this household
        for rid, room in rooms_dict.items():
            if not isinstance(room, dict):
                continue

            if (
                str(room.get("home_id")) == household_id_str
                and str(room.get("room_name", "")).strip() == area_name_str
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Area with name '{area_name_str}' already exists in household '{household_id_str}' (room_id: {rid})",
                    }
                )

        # Generate new room_id (area_id)
        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        new_room_id = generate_id(rooms_dict)

        # Create new area entry
        new_area = {
            "room_id": new_room_id,
            "home_id": household_id_str,
            "room_name": area_name_str,
            "room_type": area_type_str,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        # Add to data
        rooms_dict[new_room_id] = new_area

        new_area_return = new_area.copy()
        new_area_return["area_id"] = new_area_return.pop("room_id")
        new_area_return["household_id"] = new_area_return.pop("home_id")
        new_area_return["area_name"] = new_area_return.pop("room_name")
        new_area_return["area_type"] = new_area_return.pop("room_type")

        return json.dumps(
            {
                "success": True,
                "area": new_area_return,
                "message": f"Area '{area_name_str}' successfully created in household '{home_info.get('home_name')}' with ID: {new_room_id}",
                "household_name": home_info.get("home_name"),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_area",
                "description": (
                    "Create a new area in a household. "
                    "Validates that the household exists and the area_type is valid. "
                    "Valid area types: bedroom, kitchen, lounge, bathroom, living_room, "
                    "dining_room, garage, hallway, storage, office, custom. "
                    "Ensures area_name is unique within the household. "
                    "Returns the created area details including the generated area_id."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "area_name": {
                            "type": "string",
                            "description": "The name of the area. Must be unique within the household.",
                        },
                        "area_type": {
                            "type": "string",
                            "description": "The type of area. Accepted values: bedroom, kitchen, lounge, bathroom, living_room, dining_room, garage, hallway, storage, office, custom.",
                        },
                        "household_id": {
                            "type": "string",
                            "description": "The ID of the household to create the area in.",
                        },
                    },
                    "required": ["area_name", "area_type", "household_id"],
                },
            },
        }
