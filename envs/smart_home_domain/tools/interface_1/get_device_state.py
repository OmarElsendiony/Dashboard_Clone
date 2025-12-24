import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetDeviceState(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        device_id: str
    ) -> str:
        """
        Get the current state of a specific device including all its state attributes.
        
        Args:
            data: The data dictionary containing devices, device_states, and device_state_attributes
            device_id: The ID of the device to get state for
            
        Returns:
            JSON string with success status and device state information
        """
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })
        
        # Validate device_id is provided
        device_id = str(device_id)
        
        # Get data collections
        devices = data.get("devices", {})
        device_states = data.get("device_states", {})
        device_state_attributes = data.get("device_state_attributes", {})
        
        # Check if device exists
        if device_id not in devices:
            return json.dumps({
                "success": False,
                "error": f"Device not found: '{device_id}'"
            })
        
        # Get device information
        device_info = devices[device_id]
        
        # Find all states for this device
        device_state_records = []
        for state_id, state_data in device_states.items():
            if str(state_data.get("device_id")) == device_id:
                device_state_records.append({
                    "state_id": state_id,
                    **state_data
                })
        
        # If no states found, return device info without state
        if not device_state_records:
            return json.dumps({
                "success": True,
                "device_id": device_id,
                "device_name": device_info.get("device_name"),
                "device_type": device_info.get("device_type"),
                "status": device_info.get("status"),
                "current_state": None,
                "message": "No state records found for this device"
            })
        
        # Sort by changed_at to get the most recent state
        device_state_records.sort(key=lambda x: x.get("changed_at", ""), reverse=True)
        most_recent_state = device_state_records[0]
        state_id = most_recent_state["state_id"]
        
        # Get all attributes for the most recent state
        state_attributes = {}
        for attr_id, attr_data in device_state_attributes.items():
            if str(attr_data.get("state_id")) == state_id:
                attr_name = attr_data.get("attribute_name")
                attr_value = attr_data.get("attribute_value")
                state_attributes[attr_name] = attr_value
        
        return json.dumps({
            "success": True,
            "device_id": device_id,
            "device_name": device_info.get("device_name"),
            "device_type": device_info.get("device_type"),
            "status": device_info.get("status"),
            "current_state": {
                "state_id": state_id,
                "changed_at": most_recent_state.get("changed_at"),
                "attributes": state_attributes
            }
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_device_state",
                "description": "Get the current state of a specific device. Returns the most recent state information including all state attributes such as power status, temperature, brightness, lock state, etc. depending on the device type.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "The ID of the device to get state for"
                        }
                    },
                    "required": ["device_id"],
                },
            },
        }

