import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreateChannel(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_name: str,
        description: Optional[str] = None
    ) -> str:
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(int(max(table.keys(), key=lambda x: int(x))) + 1)
        
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for channels"
            })
        
        channels = data.get("channels", {})
        
        if not channel_name:
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: channel_name is required"
            })
        
        for channel in channels.values():
            if channel.get("channel_name") == channel_name:
                return json.dumps({
                    "success": False,
                    "error": f"Channel with name '{channel_name}' already exists"
                })
        
        new_channel_id = generate_id(channels)
        
        # Internally storing the database structure with None for the removed relations
        new_channel = {
            "channel_id": str(new_channel_id),
            "channel_name": str(channel_name),
            "description": str(description) if description is not None else None,
            "channel_type": "room",  # Hardcoded default value
            "status": "active",
            "project_id": None,
            "work_item_id": None,
            "incident_id": None,
            "created_at": "2026-02-11T23:59:00",
            "updated_at": "2026-02-11T23:59:00"
        }
        
        channels[str(new_channel_id)] = new_channel
        
        # Cleaned response omitting the IDs and channel_type
        channel_response = {
            "channel_id": str(new_channel_id),
            "channel_name": str(channel_name),
            "description": str(description) if description is not None else None,
            "status": "active",
            "created_at": "2026-02-11T23:59:00",
            "updated_at": "2026-02-11T23:59:00"
        }
        
        return json.dumps({
            "success": True,
            "message": f"Channel '{channel_name}' created successfully",
            "channel_id": str(new_channel_id),
            "channel_data": channel_response
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_channel",
                "description": "Creates a new communication channel.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_name": {
                            "type": "string",
                            "description": "Name of the channel"
                        },
                        "description": {
                            "type": "string",
                            "description": "Channel description"
                        }
                    },
                    "required": ["channel_name"]
                }
            }
        }
