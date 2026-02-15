import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class PublishResponse(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_id: str,
        message: str,
        visibility: str,
        sender_id: Optional[str] = None,
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

        if not message:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'message' is required."
            })

        if not visibility:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'visibility' is required."
            })

        if not isinstance(ticket_id, str) or not ticket_id.strip():
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: ticket_id must be a non-empty string."
            })

        if not isinstance(message, str) or not message.strip():
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: message must be a non-empty string."
            })

        if not isinstance(visibility, str) or not visibility.strip():
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: visibility must be a non-empty string."
            })

        vis = visibility.strip().lower()
        if vis not in ["internal", "public"]:
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: visibility must be 'internal' or 'public'."
            })

        if sender_id is not None and (not isinstance(sender_id, str) or not sender_id.strip()):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: sender_id must be a non-empty string when provided."
            })

        tickets = data.get("tickets", {})
        ticket_comments = data.get("ticket_comments", {})
        users = data.get("users", {})

        if not isinstance(tickets, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'tickets' must be a dictionary"
            })

        if not isinstance(ticket_comments, (dict, list)):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'ticket_comments' must be a dictionary or list"
            })

        tkey = str(ticket_id).strip()
        ticket_obj = tickets.get(tkey)

        if ticket_obj is None:
            for v in tickets.values():
                if isinstance(v, dict) and str(v.get("ticket_id", "")).strip() == tkey:
                    ticket_obj = v
                    break

        if ticket_obj is None:
            return json.dumps({
                "success": False,
                "error": f"Not Found Error: ticket_id '{ticket_id}' not found."
            })

        if sender_id is not None and isinstance(users, dict):
            if str(sender_id).strip() not in users:
                return json.dumps({
                    "success": False,
                    "error": f"Authorization Error: sender_id '{sender_id}' not found."
                })

        is_public = (vis == "public")
        timestamp = "2026-02-02 23:59:00"

        existing_numeric = []
        existing_str = set()

        if isinstance(ticket_comments, dict):
            for k in ticket_comments.keys():
                existing_str.add(str(k))
                try:
                    existing_numeric.append(int(str(k)))
                except Exception:
                    continue

            for row in ticket_comments.values():
                if isinstance(row, dict):
                    cid = row.get("comment_id")
                    if cid is not None:
                        existing_str.add(str(cid))
                        try:
                            existing_numeric.append(int(str(cid)))
                        except Exception:
                            continue

        if isinstance(ticket_comments, list):
            for row in ticket_comments:
                if isinstance(row, dict):
                    cid = row.get("comment_id")
                    if cid is not None:
                        existing_str.add(str(cid))
                        try:
                            existing_numeric.append(int(str(cid)))
                        except Exception:
                            continue

        next_id = (max(existing_numeric) + 1) if existing_numeric else (len(existing_str) + 1)
        comment_id = str(next_id)

        while comment_id in existing_str:
            next_id += 1
            comment_id = str(next_id)

        new_comment = {
            "comment_id": comment_id,
            "ticket_id": tkey,
            "sender_id": str(sender_id).strip() if sender_id is not None else "",
            "message": message.strip(),
            "is_public": is_public,
            "created_at": timestamp,
            "updated_at": timestamp
        }

        if isinstance(ticket_comments, dict):
            ticket_comments[comment_id] = new_comment

        if isinstance(ticket_comments, list):
            ticket_comments.append(new_comment)

        if isinstance(ticket_obj, dict) and "updated_at" in ticket_obj:
            ticket_obj["updated_at"] = timestamp

        return json.dumps({
            "success": True,
            "comment": new_comment,
            "visibility": vis,
            "message_text": "Comment added successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "publish_response",
                "description": (
                    "Adds a new comment to an existing Zendesk support ticket and strictly controls whether the comment is visible to the customer or only to internal support agents."

                    "PURPOSE: Facilitates explicit communication by distinguishing between public customer-facing responses and private internal documentation for agents."

                    "WHEN TO USE: When providing customer updates, requesting additional information publicly, documenting internal investigations, or coordinating privately among agents without sharing sensitive context with the requester."

                    "RETURNS: The newly created ticket comment record, including its final visibility classification and stored metadata."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "The unique ID of the Zendesk ticket to add a comment to."
                        },
                        "message": {
                            "type": "string",
                            "description": "The comment text to add to the ticket."
                        },
                        "visibility": {
                            "type": "string",
                            "enum": ["internal", "public"],
                            "description": "Visibility classification for the ticket comment."
                        },
                        "sender_id": {
                            "type": "string",
                            "description": "Identifier of the agent posting the comment (optional )"
                        }
                    },
                    "required": ["ticket_id", "message", "visibility"]
                }
            }
        }
