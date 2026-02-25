import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class FetchChannel(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        project_id: str,
        channel_name: str,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'data' must be a dict"
            })

        if not project_id:
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: 'project_id'"
            })

        if not channel_name:
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: 'channel_name'"
            })

        channels_dict = data.get("channels", {})

        if not isinstance(channels_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'channels' must be a dict"
            })

        project_id_clean = str(project_id).strip()
        channel_name_clean = str(channel_name).strip()

        matched_channel = None
        matched_channel_id = None

        for cid, channel_data in channels_dict.items():

            if str(channel_data.get("project_id", "")).strip() != project_id_clean:
                continue

            if str(channel_data.get("channel_name", "")).strip() == channel_name_clean:
                matched_channel = channel_data
                matched_channel_id = cid
                break

        if not matched_channel:
            return json.dumps({
                "success": False,
                "error": "Channel not found for the given project and channel_name"
            })

        response_channel = {
            "channel_id": str(matched_channel_id),
            "channel_name": str(matched_channel.get("channel_name", "")),
            "description": str(matched_channel.get("description", "")),
            "channel_type": str(matched_channel.get("channel_type", "")),
            "status": str(matched_channel.get("status", "")),
            "project_id": str(matched_channel.get("project_id", "")),
            "work_item_id": str(matched_channel.get("work_item_id", "")),
            "incident_id": str(matched_channel.get("incident_id", "")),
            "created_at": str(matched_channel.get("created_at", "")),
            "updated_at": str(matched_channel.get("updated_at", ""))
        }

        return json.dumps({
            "success": True,
            "channel": response_channel
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_channel",
                "description": "Retrieves communication channel details within a specific project context. "
                               "This function validates that the specified channel exists and confirms its current state "
                               "Use this before sending messages or managing communication threads in TPM workflows.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The unique identifier of the project whose channel is to be retrieved."
                        },
                        "channel_name": {
                            "type": "string",
                            "description": "The exact name of the channel to retrieve within the project."
                        }
                    },
                    "required": ["project_id", "channel_name"]
                }
            }
        }

