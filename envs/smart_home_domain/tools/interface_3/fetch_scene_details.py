import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class FetchSceneDetails(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: str,
        scene_name: str,
        scene_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        """Retrieve scene metadata for a household using scene name plus optional filters. Also returns scene actions + attributes."""
        try:
            if not isinstance(data, dict):
                return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

            scenes = data.get("scenes")
            scene_actions = data.get("scene_actions")
            scene_action_attributes = data.get("scene_action_attributes")

            if not isinstance(scenes, dict):
                return json.dumps({"success": False, "error": "Missing scenes collection in dataset."})

            if not isinstance(scene_actions, dict) or not isinstance(scene_action_attributes, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Missing scene_actions or scene_action_attributes collections in dataset.",
                    }
                )

            if not isinstance(home_id, str) or not home_id.strip():
                return json.dumps({"success": False, "error": "home_id is required for lookup."})

            if not isinstance(scene_name, str) or not scene_name.strip():
                return json.dumps({"success": False, "error": "scene_name is required for lookup."})

            home_id_clean = home_id.strip()
            scene_name_clean = scene_name.strip().lower()
            scene_id_clean = scene_id.strip() if isinstance(scene_id, str) and scene_id.strip() else None

            normalized_status = None
            if status is not None:
                if not isinstance(status, str) or not status.strip():
                    return json.dumps(
                        {"success": False, "error": "status must be 'enabled' or 'disabled' when provided."}
                    )
                normalized_status = status.strip().lower()
                if normalized_status not in {"enabled", "disabled"}:
                    return json.dumps(
                        {"success": False, "error": "status must be 'enabled' or 'disabled' when provided."}
                    )

            results = []
            for record in scenes.values():
                if not isinstance(record, dict):
                    continue

                if str(record.get("home_id", "")).strip() != home_id_clean:
                    continue

                if str(record.get("scene_name", "")).strip().lower() != scene_name_clean:
                    continue

                if scene_id_clean and str(record.get("scene_id", "")).strip() != scene_id_clean:
                    continue

                if normalized_status and str(record.get("status", "")).strip().lower() != normalized_status:
                    continue

                sid = str(record.get("scene_id", "")).strip()
                if not sid:
                    continue

                # ---- collect actions for this scene ----
                actions_for_scene = []
                for action in scene_actions.values():
                    if not isinstance(action, dict):
                        continue
                    if str(action.get("scene_id", "")).strip() != sid:
                        continue

                    scene_action_id = str(action.get("scene_action_id", "")).strip()
                    if not scene_action_id:
                        continue

                    # ---- collect attributes for this action ----
                    attrs_for_action = []
                    for attr in scene_action_attributes.values():
                        if not isinstance(attr, dict):
                            continue
                        if str(attr.get("scene_action_id", "")).strip() != scene_action_id:
                            continue

                        attrs_for_action.append(
                            {
                                "attribute_id": attr.get("attribute_id"),
                                "scene_action_id": scene_action_id,
                                "attribute_name": attr.get("attribute_name"),
                                "attribute_value": attr.get("attribute_value"),
                                "created_at": attr.get("created_at"),
                            }
                        )

                    actions_for_scene.append(
                        {
                            "scene_action_id": scene_action_id,
                            "scene_id": sid,
                            "device_id": action.get("device_id"),
                            "created_at": action.get("created_at"),
                            "attributes": attrs_for_action,
                        }
                    )

                results.append(
                    {
                        "scene_id": record.get("scene_id"),
                        "scene_name": record.get("scene_name"),
                        "status": record.get("status"),
                        "description": record.get("description"),
                        "home_id": record.get("home_id"),
                        "created_by_user_id": record.get("created_by_user_id"),
                        "created_at": record.get("created_at"),
                        "updated_at": record.get("updated_at"),
                        "actions": actions_for_scene,
                    }
                )

            if not results:
                return json.dumps({"success": False, "error": "No scenes match the provided inputs."})

            return json.dumps(
                {
                    "success": True,
                    "message": "Scenes retrieved successfully.",
                    "scenes": results,
                    "count": len(results),
                }
            )

        except Exception as exc:
            return json.dumps({"success": False, "error": f"Failed to fetch scene details: {exc}"})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_scene_details",
                "description": (
                    "Fetch scene metadata for a household using home_id and scene_name. "
                    "Also returns scene actions and action attributes for each matched scene."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "Required household identifier where the scene resides.",
                        },
                        "scene_name": {
                            "type": "string",
                            "description": "Required scene name.",
                        },
                        "scene_id": {
                            "type": "string",
                            "description": "Optional scene identifier to narrow the search to a specific record.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional status filter ('enabled' or 'disabled').",
                        },
                    },
                    "required": ["home_id", "scene_name"],
                },
            },
        }
