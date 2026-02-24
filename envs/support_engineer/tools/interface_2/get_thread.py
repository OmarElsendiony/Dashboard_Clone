import json
from typing import Any, Dict, Optional, List
from tau_bench.envs.tool import Tool


class GetThread(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_id: Optional[str] = None,
        thread_name: Optional[str] = None,
        thread_id: Optional[str] = None,
    ) -> str:
        def find_threads(
            threads_dict: Dict[str, Any],
            channel_id_str: Optional[str] = None,
            thread_name_str: Optional[str] = None,
            thread_id_str: Optional[str] = None,
        ) -> List[Dict[str, Any]]:
            matching_threads = []

            for tid, thread in threads_dict.items():
                if not isinstance(thread, dict):
                    continue

                # If thread_id is provided, return only that specific thread
                matches = True
                if thread_id_str is not None:
                    if str(tid) != thread_id_str:
                        matches = False

                if channel_id_str is not None:
                    if str(thread.get("channel_id", "")).strip() != channel_id_str:
                        matches = False

                if thread_name_str is not None:
                    if str(thread.get("thread_name", "")).strip() != thread_name_str:
                        matches = False

                if matches:
                    thread_data = thread.copy()
                    thread_data["thread_id"] = str(tid)
                    matching_threads.append(thread_data)

            return matching_threads

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        # Get data containers
        threads_dict = data.get("threads", {})
        channels_dict = data.get("channels", {})

        # Convert and validate inputs
        channel_id_str = str(channel_id).strip() if channel_id else None
        thread_name_str = str(thread_name).strip() if thread_name else None
        thread_id_str = str(thread_id).strip() if thread_id else None

        # Check at least one search parameter is provided
        if not any([channel_id, thread_name, thread_id]):
            return json.dumps({
                "success": False,
                "error": "At least one parameter (channel_id, thread_name, or thread_id) must be provided"
            })

        if channel_id_str:
            if channel_id_str not in channels_dict:
                return json.dumps({
                    "success": False,
                    "error": f"Channel with ID '{channel_id_str}' not found"
                })

            channel = channels_dict[channel_id_str]

            if not isinstance(channel, dict):
                return json.dumps({
                    "success": False,
                    "error": f"Invalid channel data structure for channel ID '{channel_id_str}'"
                })

            channel_status = str(channel.get("status", "")).strip()
            if channel_status not in ["active", "archived"]:
                return json.dumps({
                    "success": False,
                    "error": f"Channel '{channel_id_str}' has invalid status '{channel_status}'"
                })

        matching_threads = find_threads(
            threads_dict,
            channel_id_str,
            thread_name_str,
            thread_id_str
        )

        if not matching_threads:
            search_criteria = []
            if thread_id_str:
                search_criteria.append(f"thread_id='{thread_id_str}'")
            if channel_id_str:
                search_criteria.append(f"channel_id='{channel_id_str}'")
            if thread_name_str:
                search_criteria.append(f"thread_name='{thread_name_str}'")

            return json.dumps({
                "success": False,
                "error": f"No threads found matching criteria: {', '.join(search_criteria)}"
            })

        for thread in matching_threads:
            thread_channel_id = thread.get("channel_id")
            if thread_channel_id and str(thread_channel_id) in channels_dict:
                channel = channels_dict[str(thread_channel_id)]
                if isinstance(channel, dict):
                    thread["channel_name"] = str(channel.get("name", ""))
                    thread["channel_type"] = str(channel.get("channel_type", ""))
                    thread["channel_status"] = str(channel.get("status", ""))

        # Build success message
        if thread_id_str:
            message = f"Thread '{matching_threads[0].get('thread_name', thread_id_str)}' retrieved successfully"
        elif len(matching_threads) == 1:
            message = f"1 thread found matching criteria"
        else:
            message = f"{len(matching_threads)} threads found matching criteria"

        return json.dumps({
            "success": True,
            "threads": matching_threads,
            "count": len(matching_threads),
            "message": message,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_thread",
                "description": (
                    "Retrieves one or more conversation threads within communication channels. "
                    "This function searches for threads based on provided criteria and can return multiple matching results. "
                    "Use this to find threads by unique identifier, locate threads within a specific channel, "
                    "search for threads by name, or discover all threads in a channel for incident coordination. "
                    "Returns detailed thread information including status, description, and associated channel details."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "Optional. The unique identifier of the channel to search for threads within.",
                        },
                        "thread_name": {
                            "type": "string",
                            "description": "Optional. The name of the thread to search for.",
                        },
                        "thread_id": {
                            "type": "string",
                            "description": "Optional. The unique identifier of a specific thread to retrieve.",
                        },
                    },
                    "required": [],
                },
            },
        }
