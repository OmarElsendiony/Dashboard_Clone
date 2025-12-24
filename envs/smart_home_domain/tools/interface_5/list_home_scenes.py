import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class ListHomeScenes(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        status: Optional[str] = None,
    ) -> str:
        """
        List scenes in a home, optionally filtered by status.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        scenes = data.get("scenes")

        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})
        if not isinstance(scenes, dict):
            return json.dumps({"success": False, "error": "scenes store missing"})

        if not isinstance(home_name, str) or not home_name.strip():
            return json.dumps({"success": False, "error": "home_name must be provided"})
        home_name = home_name.strip()

        # Find home by name
        home_id = None
        for hid, home in homes.items():
            if home.get("home_name", "").strip().lower() == home_name.lower():
                home_id = hid
                break
        if not home_id:
            return json.dumps({"success": False, "error": f"Home '{home_name}' not found"})

        status_filter = None
        if status:
            if not isinstance(status, str):
                return json.dumps({"success": False, "error": "status must be a string"})
            status_filter = status.strip().lower()
            if status_filter not in {"enabled", "disabled"}:
                return json.dumps({"success": False, "error": "status must be one of enabled, disabled"})

        result_scenes = []
        for scene in scenes.values():
            if scene.get("home_id") == home_id:
                if status_filter and scene.get("status") != status_filter:
                    continue
                result_scenes.append({
                    "home_name": home_name,
                    "scene_id": scene.get("scene_id"),
                    "scene_name": scene.get("scene_name"),
                    "description": scene.get("description"),
                    "status": scene.get("status"),
                    "voice_control_phrase": scene.get("voice_control_phrase"),
                    "created_at": scene.get("created_at"),
                    "updated_at": scene.get("updated_at"),
                })

        return json.dumps({"success": True, "scenes": result_scenes})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_home_scenes",
                "description": "List all scenes in a home, optionally filtered by status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional status filter; allowed values: enabled, disabled.",
                        },
                    },
                    "required": ["home_name"],
                },
            },
        }

