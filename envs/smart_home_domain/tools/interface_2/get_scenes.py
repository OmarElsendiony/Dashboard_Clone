import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetScenes(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: str,
        scene_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        """
        Get scenes by various criteria.
        """
        scenes_dict = data.get("scenes", {})
        if not isinstance(scenes_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid scenes container: expected dict at data['scenes']"
            })

        homes_dict = data.get("homes", {})
        if not isinstance(homes_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid homes container: expected dict at data['homes']"
            })

        # Validate home_id exists
        if home_id not in homes_dict:
            return json.dumps({
                "success": False,
                "error": f"Home with ID '{home_id}' not found"
            })

        # Validate status if provided
        if status and status not in ["enabled", "disabled"]:
            return json.dumps({
                "success": False,
                "error": "status must be one of: 'enabled', 'disabled'"
            })

        # Filter scenes
        results = []
        for sid, scene in scenes_dict.items():
            if not isinstance(scene, dict):
                continue

            # Filter by home_id (required)
            if str(scene.get("home_id")) != str(home_id):
                continue

            # Filter by scene_id if provided
            if scene_id and str(sid) != str(scene_id):
                continue

            # Filter by status if provided
            if status and scene.get("status") != status:
                continue

            # Create scene copy with scene_id
            scene_copy = dict(scene)
            scene_copy["scene_id"] = str(sid)
            results.append(scene_copy)

        if not results:
            return json.dumps({
                "success": True,
                "count": 0,
                "results": []
            })

        return json.dumps({
            "success": True,
            "count": len(results),
            "results": results
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_scenes",
                "description": (
                    "Get scenes by home_id with optional filters for scene_id and status. "
                    "Returns all scenes for a given home, optionally filtered by scene_id and/or status (enabled/disabled)."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "The ID of the home to retrieve scenes for."
                        },
                        "scene_id": {
                            "type": "string",
                            "description": "Optional filter by specific scene ID."
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional filter by status: 'enabled' or 'disabled'."
                        }
                    },
                    "required": ["home_id"]
                }
            }
        }
