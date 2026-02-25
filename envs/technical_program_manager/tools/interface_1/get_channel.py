import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class GetChannel(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_id: Optional[str] = None,
        channel_name: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for channels"
            })
        
        channels = data.get("channels", {})
        
        if not channel_id and not channel_name:
            return json.dumps({
                "success": False,
                "error": "At least one parameter (channel_id or channel_name) must be provided"
            })
        
        found_channel = None
        found_id = None
        
        # Use Case 1: Search by channel_id
        if channel_id:
            if str(channel_id) in channels:
                found_channel = channels[str(channel_id)]
                found_id = str(channel_id)
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Channel with ID '{channel_id}' not found"
                })
            
            channel_data = {
                "channel_id": str(found_id),
                "channel_name": str(found_channel.get("channel_name", "")),
                "description": str(found_channel.get("description", "")) if found_channel.get("description") is not None else None,
                "status": str(found_channel.get("status", "")),
                "created_at": str(found_channel.get("created_at", "")),
                "updated_at": str(found_channel.get("updated_at", ""))
            }
            
            return json.dumps({
                "success": True,
                "channel_data": channel_data
            })
        
        # Use Case 2: Search by channel_name
        if channel_name:
            found_channels = []
            
            for cid, channel in channels.items():
                if channel.get("channel_name") != channel_name:
                    continue
                
                channel_data = {
                    "channel_id": str(cid),
                    "channel_name": str(channel.get("channel_name", "")),
                    "description": str(channel.get("description", "")) if channel.get("description") is not None else None,
                    "status": str(channel.get("status", "")),
                    "created_at": str(channel.get("created_at", "")),
                    "updated_at": str(channel.get("updated_at", ""))
                }
                
                found_channels.append(channel_data)
            
            if not found_channels:
                return json.dumps({
                    "success": False,
                    "error": f"No channel found with name '{channel_name}'"
                })
            
            if len(found_channels) == 1:
                return json.dumps({
                    "success": True,
                    "channel_data": found_channels[0]
                })
            
            return json.dumps({
                "success": True,
                "multiple_results": True,
                "count": int(len(found_channels)),
                "channels": found_channels
            })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_channel",
                "description": "Retrieves communication channel information. Use this to verify channel existence before posting messages or to get channel details for stakeholder communication.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "The unique identifier of the channel (optional if channel_name is provided)"
                        },
                        "channel_name": {
                            "type": "string",
                            "description": "The name of the channel (optional if channel_id is provided)"
                        }
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["channel_id"]},
                        {"required": ["channel_name"]}
                    ]
                }
            }
        }
