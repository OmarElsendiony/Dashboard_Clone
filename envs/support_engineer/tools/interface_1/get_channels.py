import json
import re
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetChannels(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        search_field: Optional[str] = None,
        query: Optional[str] = None,
        limit: Optional[int] = 25,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if search_field is not None and not isinstance(search_field, str):
            return json.dumps({"success": False, "error": "Invalid Argument: 'search_field'"})

        if query is not None and not isinstance(query, str):
            return json.dumps({"success": False, "error": "Invalid Argument: 'query'"})

        if (search_field and not query) or (not search_field and query):
            return json.dumps({
                "success": False,
                "error": "Both 'search_field' and 'query' must be provided together, or both omitted to list all channels."
            })

        try:
            limit_val = int(limit) if limit is not None else 25
            if limit_val <= 0:
                limit_val = 25
        except (ValueError, TypeError):
            limit_val = 25

        channels = data.get("channels", {})
        if not isinstance(channels, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'channels' table missing or malformed."})

        matched = []

        if search_field and query:
            valid_search_fields = [
                "channel_id",
                "name",
                "description",
                "ticket_id",
                "channel_type",
                "status",
                "created_at",
                "updated_at"
            ]

            if search_field not in valid_search_fields:
                return json.dumps({"success": False, "error": f"Invalid search_field: {search_field}. Must be one of {valid_search_fields}"})

            regex_fields = {"name", "description", "channel_type", "status"}

            try:
                pattern = re.compile(query, re.IGNORECASE) if search_field in regex_fields else None
            except re.error:
                return json.dumps({"success": False, "error": "Invalid regex pattern in query."})

            for channel in channels.values():
                if not isinstance(channel, dict):
                    continue

                raw_val = channel.get(search_field)
                target_value = "" if raw_val is None else str(raw_val)

                if search_field in regex_fields:
                    if pattern.search(target_value):
                        matched.append(channel)
                else:
                    if target_value == str(query):
                        matched.append(channel)
        else:
            for channel in channels.values():
                if isinstance(channel, dict):
                    matched.append(channel)

        matched.sort(key=lambda x: (
            str(x.get("name", "")).lower(),
            str(x.get("channel_id", ""))
        ))

        matched = matched[:limit_val]

        formatted_channels = []
        for c in matched:
            formatted_channels.append({
                "channel_id": str(c.get("channel_id", "")),
                "name": str(c.get("name", "")),
                "description": str(c.get("description", "")),
                "ticket_id": str(c.get("ticket_id", "")) if c.get("ticket_id") is not None else "",
                "channel_type": str(c.get("channel_type", "")),
                "status": str(c.get("status", "")),
                "created_at": str(c.get("created_at", "")),
                "updated_at": str(c.get("updated_at", ""))
            })

        return json.dumps({
            "success": True,
            "channels": formatted_channels,
            "returned_count": len(formatted_channels),
            "matched_count": len(matched),
            "message": "Channels retrieved successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_channels",
                "description": (
                    "Retrieves communication channel records from the database by querying specific metadata fields. It can also list all available channels if search parameters are omitted.\n"
                    " Purpose: Used to discover channels for incident communication, general discussion, and broadcasting. It directly supports the 'Broadcast Updates' SOP by allowing an agent to fetch the 'public' channel associated with a specific ticket.\n"
                    " When to use: Use this tool whenever you need to find a communication channel. For example, search by 'ticket_id' to find the channel linked to an ongoing incident, or search by 'channel_type' to find all 'public' broadcast channels.\n"
                    " Returns: Returns a JSON string containing a success flag, a list of channel metadata dictionaries, and record counts. "
                    "Default behavior: 'limit' defaults to 25. If 'search_field' and 'query' are omitted, it returns all channels up to the limit. "
                    "Search behavior: Case-insensitive regex searching is supported for 'name', 'description', 'channel_type', and 'status'. "
                    "Strict exact string matching is required for 'channel_id', 'ticket_id', 'created_at', and 'updated_at'."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_field": {
                            "type": "string",
                            "enum": [
                                "channel_id",
                                "name",
                                "description",
                                "ticket_id",
                                "channel_type",
                                "status",
                                "created_at",
                                "updated_at"
                            ],
                            "description": "The specific field in the channels table to search within."
                        },
                        "query": {
                            "type": "string",
                            "description": "The exact value or regex pattern to search for. Regex is evaluated case-insensitively for name, description, channel_type, and status."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "The maximum number of channel records to return. Defaults to 25."
                        }
                    },
                    "required": []
                }
            }
        }
