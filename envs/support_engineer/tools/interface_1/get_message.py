import json
import re
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetMessage(Tool):
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
            return json.dumps({"success": False, "error": "Both 'search_field' and 'query' must be provided together, or both omitted to list all messages."})

        if limit is None:
            limit = 25

        if not isinstance(limit, int) or limit <= 0:
            return json.dumps({"success": False, "error": "Invalid Argument: 'limit'"})

        channel_messages = data.get("channel_messages", {})
        if not isinstance(channel_messages, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'channel_messages'"})

        matched = []

        if search_field and query:
            valid_search_fields = [
                "message_id",
                "channel_id",
                "thread_id",
                "sender_id",
                "message",
                "related_ticket_id",
                "sent_at",
                "created_at",
                "updated_at"
            ]

            if search_field not in valid_search_fields:
                return json.dumps({"success": False, "error": f"Invalid search_field: {search_field}, can only be {valid_search_fields}"})

            regex_fields = {"message"}

            try:
                pattern = re.compile(query, re.IGNORECASE) if search_field in regex_fields else None
            except re.error:
                return json.dumps({"success": False, "error": "Invalid regex pattern in query"})

            for msg in channel_messages.values():
                if not isinstance(msg, dict):
                    continue

                target_value = str(msg.get(search_field, ""))

                if search_field in regex_fields:
                    if pattern.search(target_value):
                        matched.append(msg)
                else:
                    if target_value == query:
                        matched.append(msg)
        else:
            for msg in channel_messages.values():
                if isinstance(msg, dict):
                    matched.append(msg)

        matched = matched[:limit]

        messages = []
        for m in matched:
            messages.append({
                "message_id": str(m.get("message_id", "")),
                "channel_id": str(m.get("channel_id", "")),
                "thread_id": str(m.get("thread_id", "")),
                "sender_id": str(m.get("sender_id", "")),
                "message": str(m.get("message", "")),
                "related_ticket_id": str(m.get("related_ticket_id", "")),
                "sent_at": str(m.get("sent_at", "")),
                "created_at": str(m.get("created_at", "")),
                "updated_at": str(m.get("updated_at", ""))
            })

        return json.dumps({
            "success": True,
            "messages": messages,
            "returned_count": len(messages),
            "matched_count": len(matched),
            "message_text": "Messages retrieved successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_message",
                "description": (
                    " Retrieves Slack messages by querying a specific search field. Can also return a list of all messages if no search parameters are provided.\n"
                    " Purpose: To filter and retrieve specific communication records for incident investigation, ticket analysis, auditing, or historical conversation lookup based on exact matches or regex patterns.\n"
                    " When to use: Use this tool when you need to find one or multiple messages using specific criteria, such as searching for keywords within a message body, finding all messages in a specific channel, retrieving messages sent by a specific user, or getting a generic list of messages.\n"
                    " Returns: Returns a JSON string containing a success boolean, a list of matching message dictionaries with their metadata, the returned count, and a success message text. "
                    "Default behavior: 'limit' defaults to 25 if not provided. If 'search_field' and 'query' are omitted, it lists all available messages up to the limit. "
                    "Regex search is supported and evaluated (case-insensitive) for the following search_field: 'message'. "
                    "Exact string match is strictly required for the following search_fields: 'message_id', 'channel_id', 'thread_id', 'sender_id', 'related_ticket_id', 'sent_at', 'created_at', and 'updated_at'."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_field": {
                            "type": "string",
                            "enum": [
                                "message_id",
                                "channel_id",
                                "thread_id",
                                "sender_id",
                                "message",
                                "related_ticket_id",
                                "sent_at",
                                "created_at",
                                "updated_at"
                            ],
                            "description": "The specific field to search within. Optional; if omitted alongside query, the tool lists all messages."
                        },
                        "query": {
                            "type": "string",
                            "description": "The value or regex pattern to search for in the specified search field. Regex is supported for the 'message' field. Exact match is used for message_id, channel_id, thread_id, sender_id, related_ticket_id, sent_at, created_at, and updated_at. Optional; if omitted alongside search_field, the tool lists all messages."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of messages to return. Default is 25."
                        }
                    },
                    "required": []
                }
            }
        }
