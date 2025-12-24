import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class UpdateArea(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        area_id: str,
        area_name: str,
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
        if not area_id:
            return json.dumps({"success": False, "error": "area_id is required"})

        if not area_name:
            return json.dumps({"success": False, "error": "area_name is required"})

        # Convert to strings for consistent comparison
        area_id_str = str(area_id).strip()
        area_name_str = str(area_name).strip()

        # Check if area exists
        if area_id_str not in rooms_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Area with ID '{area_id_str}' not found",
                }
            )

        area = rooms_dict[area_id_str]
        if not isinstance(area, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid area data for ID '{area_id_str}'",
                }
            )

        # Get household_id from the area
        household_id_str = str(area.get("home_id"))

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

        # Check if new area_name conflicts with existing areas (excluding current area)
        for rid, room in rooms_dict.items():
            if not isinstance(room, dict):
                continue

            # Skip the current area being updated
            if str(rid) == area_id_str:
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

        # Store old name for message
        old_area_name = area.get("room_name")

        # Update area name
        area["room_name"] = area_name_str
        area["updated_at"] = timestamp

        area_return = area.copy()
        area_return["area_id"] = area_return.pop("room_id")
        area_return["area_name"] = area_return.pop("room_name")
        area_return["area_type"] = area_return.pop("room_type")
        area_return["household_id"] = area_return.pop("home_id")

        return json.dumps(
            {
                "success": True,
                "area": area_return,
                "message": f"Area '{old_area_name}' successfully renamed to '{area_name_str}'.",
                "household_name": home_info.get("home_name"),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_area",
                "description": (
                    "Update area information by renaming the area. "
                    "Validates that the area exists. "
                    "Ensures the new area_name is unique within the household (excluding the current area). "
                    "Returns the updated area details including area_id,  area_name, "
                    "area_type, home_id, and timestamps."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "area_id": {
                            "type": "string",
                            "description": "The ID of the area to update.",
                        },
                        "area_name": {
                            "type": "string",
                            "description": "The new name for the area. Must be unique within the household.",
                        },
                    },
                    "required": ["area_id", "area_name"],
                },
            },
        }