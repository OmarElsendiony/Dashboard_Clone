import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class FetchArea(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        area_name: str,
        household_id: str,
    ) -> str:
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

        if not household_id:
            return json.dumps({"success": False, "error": "household_id is required"})

        # Convert to strings for consistent comparison
        area_name_str = str(area_name).strip()
        household_id_str = str(household_id).strip()

        # Check if household exists
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

        # Find area by name in the specified household
        area_id = None
        area_info = None
        for rid, room in rooms_dict.items():
            if not isinstance(room, dict):
                continue

            if (
                str(room.get("home_id")) == household_id_str
                and str(room.get("room_name", "")).strip() == area_name_str
            ):
                area_id = str(rid)
                area_info = room.copy()
                area_info["room_id"] = area_id
                break

        if area_info is None:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Area with name '{area_name_str}' not found in household '{household_id_str}'",
                }
            )
        
        area_info_return = area_info.copy()
        area_info_return["area_id"] = area_info_return.pop("room_id")
        area_info_return["area_name"] = area_info_return.pop("room_name")
        area_info_return["area_type"] = area_info_return.pop("room_type")
        area_info_return["household_id"] = area_info_return.pop("home_id")
        area_info_return["area_description"] = area_info_return.pop("room_description")        

        return json.dumps(
            {
                "success": True,
                "area": area_info_return,
                "message": f"Area '{area_name_str}' found successfully in household '{home_info.get('home_name')}'",
                "household_name": home_info.get("home_name"),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """
        Tool schema for function-calling.
        """
        return {
            "type": "function",
            "function": {
                "name": "fetch_area",
                "description": (
                    "Retrieve area information by area name and household ID. "
                    "Returns area details including area_id, area_name, "
                    "area_type, home_id, and timestamps. "
                    "Valid area types include: bedroom, kitchen, lounge, bathroom, living_room, "
                    "dining_room, garage, hallway, storage, office, custom. "
                    "Validates that the household exists. "
                    "Returns an error if the household doesn't exist or the area is not found in the specified household."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "area_name": {
                            "type": "string",
                            "description": "The name of the area to retrieve.",
                        },
                        "household_id": {
                            "type": "string",
                            "description": "The ID of the household where the area is located.",
                        },
                    },
                    "required": ["area_name", "household_id"],
                },
            },
        }
