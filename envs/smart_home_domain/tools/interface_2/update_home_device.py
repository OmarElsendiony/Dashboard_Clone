import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdateHomeDevice(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        device_id: str,
        device_name: Optional[str] = None,
        device_type: Optional[str] = None,
        serial_number: Optional[str] = None,
        room_id: Optional[str] = None,
        status: Optional[str] = None,
        support_automation: Optional[bool] = None,
        favorite: Optional[bool] = None,
        user_id: Optional[str] = None,
        home_id: Optional[str] = None
    ) -> str:
        """
        Update an existing device in the smart home system.
        
        Args:
            data: The data dictionary containing all smart home data.
            device_id: The device ID to update (required).
            device_name: Updated device name (optional).
            device_type: Updated device type (optional).
            serial_number: Updated serial number (optional).
            room_id: Updated room ID (optional).
            status: Updated status (optional).
            support_automation: Updated automation support flag (optional).
            favorite: If True and user_id/home_id provided, add to favorites; if False, remove from favorites (optional).
            user_id: User ID for favorite operations (optional, required if favorite is set).
            home_id: Home ID for the device or favorite operations (optional).
            
        Returns:
            JSON string containing the success status and updated device information.
        """
        devices = data.get("devices", {})
        user_home_favorite_devices = data.setdefault("user_home_favorite_devices", {})
        
        timestamp = "2025-12-19T23:59:00"
        
        # Check if device exists
        device = devices.get(device_id)
        if not device:
            return json.dumps({
                "success": False,
                "error": f"Device ID {device_id} not found"
            })
        
        # Update device fields
        if device_name is not None:
            device["device_name"] = device_name
        if device_type is not None:
            device["device_type"] = device_type
        if serial_number is not None:
            device["serial_number"] = serial_number
        if room_id is not None:
            device["room_id"] = str(room_id) if room_id else None
        if status is not None:
            device["status"] = status
            # Update last_seen based on status
            if status == "online":
                device["last_seen"] = timestamp
        if support_automation is not None:
            device["support_automation"] = support_automation
        if home_id is not None:
            device["home_id"] = str(home_id)
        
        device["updated_at"] = timestamp
        
        # Handle favorite operations
        favorite_data = None
        if favorite is not None and user_id is not None:
            actual_home_id = home_id if home_id is not None else device.get("home_id")
            
            if favorite:
                # Add to favorites
                # Check if already exists
                existing_fav = None
                for fav_id, fav_data in user_home_favorite_devices.items():
                    if (fav_data.get("user_id") == str(user_id) and 
                        fav_data.get("home_id") == str(actual_home_id) and 
                        fav_data.get("device_id") == device_id):
                        existing_fav = fav_id
                        break
                
                if not existing_fav:
                    # Generate new favorite ID
                    if user_home_favorite_devices:
                        max_fav_id = max([int(k) for k in user_home_favorite_devices.keys()])
                        new_fav_id = str(max_fav_id + 1)
                    else:
                        new_fav_id = "1"
                    
                    # Create new favorite entry
                    new_favorite = {
                        "preference_id": new_fav_id,
                        "user_id": str(user_id),
                        "home_id": str(actual_home_id),
                        "favorite_name": device.get("device_name"),
                        "device_id": device_id,
                        "created_at": timestamp,
                        "updated_at": timestamp,
                        "preference_description": f"User {user_id}'s favorite: {device.get('device_name')}"
                    }
                    user_home_favorite_devices[new_fav_id] = new_favorite
                    favorite_data = {"action": "added", "favorite": new_favorite}
                else:
                    favorite_data = {"action": "already_exists", "favorite": dict(user_home_favorite_devices[existing_fav])}
            else:
                # Remove from favorites
                removed_favorites = []
                fav_to_remove = []
                for fav_id, fav_data in user_home_favorite_devices.items():
                    if (fav_data.get("user_id") == str(user_id) and 
                        fav_data.get("home_id") == str(actual_home_id) and 
                        fav_data.get("device_id") == device_id):
                        fav_to_remove.append(fav_id)
                        removed_favorites.append(dict(fav_data))
                
                for fav_id in fav_to_remove:
                    del user_home_favorite_devices[fav_id]
                
                if removed_favorites:
                    favorite_data = {"action": "removed", "favorites": removed_favorites}
                else:
                    favorite_data = {"action": "not_in_favorites"}
        
        # Return the complete updated device with success status
        result = {
            "success": True,
            **dict(device)
        }
        
        if favorite_data:
            result["favorite_operation"] = favorite_data
        
        return json.dumps(result)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_home_device",
                "description": "Update an existing device in the smart home system. Can update device properties and manage favorite status. If favorite is True, adds device to user's favorites; if False, removes it. Requires user_id and home_id for favorite operations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "The device ID to update (required)."
                        },
                        "device_name": {
                            "type": "string",
                            "description": "Updated device name (optional)."
                        },
                        "device_type": {
                            "type": "string",
                            "description": "Updated device type (optional)."
                        },
                        "serial_number": {
                            "type": "string",
                            "description": "Updated serial number (optional)."
                        },
                        "room_id": {
                            "type": "string",
                            "description": "Updated room ID (optional)."
                        },
                        "status": {
                            "type": "string",
                            "enum": ["online", "offline"],
                            "description": "Updated device status (optional)."
                        },
                        "support_automation": {
                            "type": "boolean",
                            "description": "Updated automation support flag (optional)."
                        },
                        "favorite": {
                            "type": "boolean",
                            "description": "If True, add device to favorites; if False, remove from favorites. Requires user_id (optional)."
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User ID for favorite operations (optional, required if favorite is set)."
                        },
                        "home_id": {
                            "type": "string",
                            "description": "Home ID for the device or favorite operations (optional)."
                        }
                    },
                    "required": ["device_id"]
                }
            }
        }
