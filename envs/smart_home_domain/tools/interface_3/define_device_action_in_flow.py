import json
from typing import Any, Dict, List
from tau_bench.envs.tool import Tool


class DefineDeviceActionInFlow(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        flow_id: str,
        action_type: str,
        target_device_id: str = None,
        target_scene_id: str = None,
        target_notification_id: str = None,
    ) -> str:
        """
        Add a routine action row for the specified Flow (routine_id). Supports only schema-defined action_type values:
        device_control, scene_activation, notification. Validates the target references according to the action type.
        """
        try:
            if not isinstance(data, dict):
                return json.dumps({"success": False, "error": "Smart Home dataset must be a dictionary."})

            flows = data.get("routines")
            devices = data.get("devices")
            scenes = data.get("scenes")
            notifications = data.get("notifications")
            actions = data.get("routine_actions")
            if not all(isinstance(tbl, dict) for tbl in (flows, devices, scenes, notifications, actions)):
                return json.dumps({"success": False, "error": "Required tables (routines/devices/scenes/notifications/routine_actions) missing or invalid."})

            if not isinstance(flow_id, str) or not flow_id.strip():
                return json.dumps({"success": False, "error": "flow_id is required."})
            flow_record = flows.get(flow_id.strip())
            if not isinstance(flow_record, dict):
                return json.dumps({"success": False, "error": "Flow not found."})

            allowed_types = {"device_control", "scene_activation", "notification"}
            if not isinstance(action_type, str) or action_type.strip().lower() not in allowed_types:
                return json.dumps({"success": False, "error": "action_type must be one of device_control, scene_activation, notification."})
            action_type_clean = action_type.strip().lower()

            target_device = None
            if action_type_clean == "device_control":
                if not isinstance(target_device_id, str) or not target_device_id.strip():
                    return json.dumps({"success": False, "error": "target_device_id is required for device_control actions."})
                target_device = devices.get(target_device_id.strip())
                if not isinstance(target_device, dict):
                    return json.dumps({"success": False, "error": "target_device_id not found."})
            elif target_device_id is not None:
                if not isinstance(target_device_id, str) or not target_device_id.strip():
                    return json.dumps({"success": False, "error": "target_device_id cannot be empty when provided."})
                target_device = devices.get(target_device_id.strip())
                if not isinstance(target_device, dict):
                    return json.dumps({"success": False, "error": "target_device_id not found."})

            target_scene = None
            if action_type_clean == "scene_activation":
                if not isinstance(target_scene_id, str) or not target_scene_id.strip():
                    return json.dumps({"success": False, "error": "target_scene_id is required for scene_activation actions."})
                target_scene = scenes.get(target_scene_id.strip())
                if not isinstance(target_scene, dict):
                    return json.dumps({"success": False, "error": "target_scene_id not found."})
            elif target_scene_id is not None:
                if not isinstance(target_scene_id, str) or not target_scene_id.strip():
                    return json.dumps({"success": False, "error": "target_scene_id cannot be empty when provided."})
                target_scene = scenes.get(target_scene_id.strip())
                if not isinstance(target_scene, dict):
                    return json.dumps({"success": False, "error": "target_scene_id not found."})

            target_notification = None
            if action_type_clean == "notification":
                if not isinstance(target_notification_id, str) or not target_notification_id.strip():
                    return json.dumps({"success": False, "error": "target_notification_id is required for notification actions."})
                target_notification = notifications.get(target_notification_id.strip())
                if not isinstance(target_notification, dict):
                    return json.dumps({"success": False, "error": "target_notification_id not found."})
            elif target_notification_id is not None:
                if not isinstance(target_notification_id, str) or not target_notification_id.strip():
                    return json.dumps({"success": False, "error": "target_notification_id cannot be empty when provided."})
                target_notification = notifications.get(target_notification_id.strip())
                if not isinstance(target_notification, dict):
                    return json.dumps({"success": False, "error": "target_notification_id not found."})

            numeric_ids: List[int] = []
            for key in actions.keys():
                try:
                    numeric_ids.append(int(key))
                except (TypeError, ValueError):
                    continue
            new_action_id = str(max(numeric_ids, default=0) + 1)

            record = {
                "action_id": new_action_id,
                "flow_id": flow_id.strip(),
                "action_type": action_type_clean,
                "target_device_id": target_device_id.strip() if target_device_id else None,
                "target_scene_id": target_scene_id.strip() if target_scene_id else None,
                "target_notification_id": target_notification_id.strip() if target_notification_id else None,
                "created_at": "2025-12-19T23:59:00",
                "updated_at": "2025-12-19T23:59:00",
            }
            actions[new_action_id] = record

            return json.dumps({"success": True, "action": record})
        except Exception as exc:
            return json.dumps({"success": False, "error": f"define_device_action_in_flow failed: {exc}"})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "define_device_action_in_flow",
                "description": (
                    "Add a device_control, scene_activation, or notification action to a Flow. "
                    "Requires flow_id and action_type, plus the corresponding target identifier."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "flow_id": {
                            "type": "string",
                            "description": "Required. Flow ID.",
                        },
                        "action_type": {
                            "type": "string",
                            "description": "Required. Enum value: device_control, scene_activation, or notification.",
                        },
                        "target_device_id": {
                            "type": "string",
                            "description": "Required when action_type=device_control. Device identifier to control.",
                        },
                        "target_scene_id": {
                            "type": "string",
                            "description": "Required when action_type=scene_activation. Scene identifier to trigger.",
                        },
                        "target_notification_id": {
                            "type": "string",
                            "description": "Required when action_type=notification. Notification identifier to send.",
                        },
                    },
                    "required": ["flow_id", "action_type"],
                },
            },
        }
