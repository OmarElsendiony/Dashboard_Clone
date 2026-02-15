import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetComments(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_id: str,
        public_only: Optional[bool] = False,
        limit: Optional[int] = None,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })

        if not ticket_id:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'ticket_id' is required."
            })

        if not isinstance(ticket_id, str) or not ticket_id.strip():
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: ticket_id must be a non-empty string."
            })

        if public_only is None:
            public_only = False

        if not isinstance(public_only, bool):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: public_only must be a boolean."
            })

        if limit is not None:
            if not isinstance(limit, int) or limit < 1:
                return json.dumps({
                    "success": False,
                    "error": "Invalid Argument: limit must be a positive integer when provided."
                })

        tickets = data.get("tickets", {})
        ticket_comments = data.get("ticket_comments", {})

        if not isinstance(tickets, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'tickets' must be a dictionary"
            })

        if not isinstance(ticket_comments, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'ticket_comments' must be a dictionary"
            })

        tkey = str(ticket_id).strip()
        if tkey not in tickets:
            return json.dumps({
                "success": False,
                "error": f"Not Found Error: ticket_id '{ticket_id}' not found."
            })

        collected = []

        for c in ticket_comments.values():
            if not isinstance(c, dict):
                continue

            if str(c.get("ticket_id", "")).strip() != tkey:
                continue

            if public_only and c.get("is_public") is not True:
                continue

            created_at = str(c.get("created_at", ""))
            comment_id = str(c.get("comment_id", ""))

            numeric_id = None
            try:
                numeric_id = int(comment_id)
            except Exception:
                numeric_id = None

            collected.append({
                "_sort_created_at": created_at,
                "_sort_numeric_id": numeric_id,
                "_sort_comment_id": comment_id,
                "_comment": c
            })

        collected.sort(
            key=lambda x: (
                x["_sort_created_at"],
                0 if x["_sort_numeric_id"] is not None else 1,
                x["_sort_numeric_id"] if x["_sort_numeric_id"] is not None else 0,
                x["_sort_comment_id"]
            )
        )

        comments = [x["_comment"] for x in collected]

        if limit is not None:
            comments = comments[:limit]

        return json.dumps({
            "success": True,
            "ticket_id": tkey,
            "comments": comments,
            "count": len(comments),
            "message": "Ticket comments retrieved successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_comments",
                "description": (
                    "Retrieves the full comment and reply history for a support ticket in chronological order."
                    "PURPOSE: Provides complete visibility into customer and agent communication on a ticket."
                    "WHEN TO USE: When auditing conversations, summarizing ticket history, reviewing troubleshooting steps, or preparing escalations."
                    "RETURNS: An ordered list of ticket comments, including public and internal notes."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "The unique ID of the ticket whose comments should be retrieved."
                        },
                        "public_only": {
                            "type": "boolean",
                            "description": "Return only public comments (optional )"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of comments to return (optional )"
                        }
                    },
                    "required": ["ticket_id"]
                }
            }
        }
