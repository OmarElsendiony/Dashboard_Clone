import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class SendSlackMessage(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_id: str,
        sender_id: str,
        message: str,
        thread_id: Optional[str] = None,
        related_ticket_id: Optional[str] = None,
        sent_at: Optional[str] = None,
        require_membership: Optional[bool] = True,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not channel_id:
            return json.dumps({"success": False, "error": "Missing Argument: 'channel_id' is required."})

        if not sender_id:
            return json.dumps({"success": False, "error": "Missing Argument: 'sender_id' is required."})

        if not message:
            return json.dumps({"success": False, "error": "Missing Argument: 'message' is required."})

        if not isinstance(channel_id, str) or not channel_id.strip():
            return json.dumps({"success": False, "error": "Invalid Argument: channel_id must be a non-empty string."})

        if not isinstance(sender_id, str) or not sender_id.strip():
            return json.dumps({"success": False, "error": "Invalid Argument: sender_id must be a non-empty string."})

        if not isinstance(message, str) or not message.strip():
            return json.dumps({"success": False, "error": "Invalid Argument: message must be a non-empty string."})

        if thread_id is not None and (not isinstance(thread_id, str) or not thread_id.strip()):
            return json.dumps({"success": False, "error": "Invalid Argument: thread_id must be a non-empty string when provided."})

        if related_ticket_id is not None and (not isinstance(related_ticket_id, str) or not related_ticket_id.strip()):
            return json.dumps({"success": False, "error": "Invalid Argument: related_ticket_id must be a non-empty string when provided."})

        if sent_at is not None and (not isinstance(sent_at, str) or not sent_at.strip()):
            return json.dumps({"success": False, "error": "Invalid Argument: sent_at must be a non-empty string when provided."})

        if require_membership is None:
            require_membership = True

        if not isinstance(require_membership, bool):
            return json.dumps({"success": False, "error": "Invalid Argument: require_membership must be a boolean."})

        channels = data.get("channels", {})
        channel_members = data.get("channel_members", {})
        channel_messages = data.get("channel_messages", {})
        users = data.get("users", {})
        tickets = data.get("tickets", {})

        if not isinstance(channels, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'channels' must be a dictionary"})

        if not isinstance(channel_members, (dict, list)):
            return json.dumps({"success": False, "error": "Invalid data format: 'channel_members' must be a dictionary or list"})

        if not isinstance(channel_messages, (dict, list)):
            return json.dumps({"success": False, "error": "Invalid data format: 'channel_messages' must be a dictionary or list"})

        if not isinstance(users, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'users' must be a dictionary"})

        cid = channel_id.strip()
        sid = sender_id.strip()

        if sid not in users:
            return json.dumps({
                "success": False,
                "error": f"Authorization Error: sender_id '{sender_id}' not found."
            })

        if cid not in channels:
            return json.dumps({
                "success": False,
                "error": f"Foreign Key Error: channel_id '{channel_id}' not found."
            })

        channel_obj = channels.get(cid, {})
        if isinstance(channel_obj, dict):
            if channel_obj.get("status") == "archived":
                return json.dumps({
                    "success": False,
                    "error": f"Invalid Operation: channel_id '{channel_id}' is archived."
                })

        channel_type = ""
        if isinstance(channel_obj, dict):
            channel_type = str(channel_obj.get("channel_type", "")).strip()

        if require_membership and channel_type in ["private", "direct"]:
            pairs = set()
            rows = channel_members.values() if isinstance(channel_members, dict) else channel_members
            for row in rows:
                if not isinstance(row, dict):
                    continue
                pairs.add((str(row.get("channel_id", "")), str(row.get("user_id", ""))))
            if (cid, sid) not in pairs:
                return json.dumps({
                    "success": False,
                    "error": f"Authorization Error: sender_id '{sender_id}' is not a member of channel '{channel_id}'."
                })

        if related_ticket_id is not None and isinstance(tickets, dict):
            if str(related_ticket_id).strip() not in tickets:
                return json.dumps({
                    "success": False,
                    "error": f"Foreign Key Error: related_ticket_id '{related_ticket_id}' not found."
                })

        timestamp = "2026-02-02 23:59:00"
        final_sent_at = sent_at.strip() if isinstance(sent_at, str) and sent_at.strip() else timestamp

        existing_ids = set()
        numeric_ids = []

        if isinstance(channel_messages, dict):
            for k in channel_messages.keys():
                existing_ids.add(str(k))
                try:
                    numeric_ids.append(int(str(k)))
                except Exception:
                    continue

            for row in channel_messages.values():
                if isinstance(row, dict) and row.get("message_id") is not None:
                    mid = str(row.get("message_id"))
                    existing_ids.add(mid)
                    try:
                        numeric_ids.append(int(mid))
                    except Exception:
                        continue

        if isinstance(channel_messages, list):
            for row in channel_messages:
                if isinstance(row, dict) and row.get("message_id") is not None:
                    mid = str(row.get("message_id"))
                    existing_ids.add(mid)
                    try:
                        numeric_ids.append(int(mid))
                    except Exception:
                        continue

        next_id = (max(numeric_ids) + 1) if numeric_ids else (len(existing_ids) + 1)
        new_message_id = str(next_id)
        while new_message_id in existing_ids:
            next_id += 1
            new_message_id = str(next_id)

        new_row = {
            "message_id": new_message_id,
            "channel_id": cid,
            "thread_id": thread_id.strip() if isinstance(thread_id, str) and thread_id.strip() else "",
            "sender_id": sid,
            "message": message.strip(),
            "related_ticket_id": related_ticket_id.strip() if isinstance(related_ticket_id, str) and related_ticket_id.strip() else "",
            "sent_at": final_sent_at,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        if isinstance(channel_messages, dict):
            channel_messages[new_message_id] = new_row
        else:
            channel_messages.append(new_row)

        if isinstance(channel_obj, dict) and "updated_at" in channel_obj:
            channel_obj["updated_at"] = timestamp

        return json.dumps({
            "success": True,
            "message": new_row,
            "message_text": "Slack message sent successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "send_slack_message",
                "description": (
                    "Posts a message to a Slack channel to keep everyone in the loop during an incident or update."

                    "PURPOSE: To create a permanent, traceable record of a conversation that can be pinned, reacted to, or used for later audits."

                    "WHEN TO USE: When you need to share triage decisions, status updates, or threaded replies, and want to keep that chat linked to a specific Zendesk ticket."

                    "RETURNS: The full message details, including its ID and timestamp, so you can track or reference it later."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "Slack channel identifier where the message should be posted."
                        },
                        "sender_id": {
                            "type": "string",
                            "description": "Slack user identifier of the sender posting the message."
                        },
                        "message": {
                            "type": "string",
                            "description": "Message text content to post into the channel."
                        },
                        "thread_id": {
                            "type": "string",
                            "description": "Thread identifier to post as a reply within a thread (optional )"
                        },
                        "related_ticket_id": {
                            "type": "string",
                            "description": "Zendesk ticket identifier to associate with the message (optional )"
                        },
                        "sent_at": {
                            "type": "string",
                            "description": "Message timestamp to store for retrieval by channel and timestamp (optional )"
                        },
                        "require_membership": {
                            "type": "boolean",
                            "description": "Enforce membership checks for private or direct channels (optional )"
                        }
                    },
                    "required": ["channel_id", "sender_id", "message"]
                }
            }
        }
