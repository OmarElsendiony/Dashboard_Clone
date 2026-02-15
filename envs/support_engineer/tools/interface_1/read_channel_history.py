import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class ReadChannelHistory(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_id: str,
        limit: Optional[int] = 50,
        thread_id: Optional[int] = None,
        oldest: Optional[str] = None,
        latest: Optional[str] = None,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not channel_id:
            return json.dumps({"success": False, "error": "Missing Argument: 'channel_id' is required."})

        channels = data.get("channels", {})
        messages = data.get("channel_messages", {})

        if channel_id not in channels:
             return json.dumps({
                "success": False,
                "error": f"Channel Error: The channel identifier '{channel_id}' does not exist."
            })

        results = []

        for msg_data in messages.values():

            if msg_data.get("channel_id") != channel_id:
                continue

            if thread_id is not None:
                msg_thread = msg_data.get("thread_id")
                if str(msg_thread) != str(thread_id):
                    continue

            msg_time = msg_data.get("created_at")
            if oldest and msg_time < oldest:
                continue
            if latest and msg_time > latest:
                continue

            results.append(msg_data)

        results.sort(key=lambda x: x.get("created_at", ""))

        final_limit = limit if limit else 50
        if len(results) > final_limit:
            results = results[-final_limit:]

        return json.dumps({
            "success": True,
            "count": len(results),
            "messages": results
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "read_channel_history",
                "description": (
                    "Retrieves a chronological list of messages from a specified channel or thread. "
                    "PURPOSE: Allows the Support Engineer to access the historical record of team communications to establish context, review previous troubleshooting steps, or audit decisions. "
                    "WHEN TO USE: 1) Catching up on an ongoing incident. 2) Reviewing the history of a specific conversation thread. 3) Gathering evidence for Post-Incident Reviews. "
                    "RETURNS: A JSON object containing a 'success' boolean, count, and a chronologically sorted list of message objects."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "REQUIRED. The unique identifier of the communication channel. Must be a valid, active channel ID."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "OPTIONAL. The maximum number of messages to retrieve. Defaults to 50. Use lower limits for quick checks and higher limits for deep audits."
                        },
                        "thread_id": {
                            "type": "integer",
                            "description": "OPTIONAL. The unique numeric identifier of the thread. If provided, filters messages to include only those belonging to this specific thread conversation."
                        },
                        "oldest": {
                            "type": "string",
                            "description": "OPTIONAL. ISO 8601 timestamp string. Only retrieve messages created AFTER this time."
                        },
                        "latest": {
                            "type": "string",
                            "description": "OPTIONAL. ISO 8601 timestamp string. Only retrieve messages created BEFORE this time."
                        }
                    },
                    "required": ["channel_id"]
                }
            }
        }
