import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ManageReaction(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        action: str,
        channel_id: str,
        sent_at: str,
        emoji: str,
        user_id: str,
        thread_id: Optional[str] = None,
        require_membership: Optional[bool] = True,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not action:
            return json.dumps({"success": False, "error": "Missing Argument: 'action' is required."})

        if not channel_id:
            return json.dumps({"success": False, "error": "Missing Argument: 'channel_id' is required."})

        if not sent_at:
            return json.dumps({"success": False, "error": "Missing Argument: 'sent_at' is required."})

        if not emoji:
            return json.dumps({"success": False, "error": "Missing Argument: 'emoji' is required."})

        if not user_id:
            return json.dumps({"success": False, "error": "Missing Argument: 'user_id' is required."})

        if not isinstance(action, str) or not action.strip():
            return json.dumps({"success": False, "error": "Invalid Argument: action must be a non-empty string."})

        action_norm = action.strip().lower()
        valid_actions = ["add", "remove"]
        if action_norm not in valid_actions:
            return json.dumps({
                "success": False,
                "error": f"Invalid Argument: action must be one of {valid_actions}."
            })

        if not isinstance(channel_id, str) or not channel_id.strip():
            return json.dumps({"success": False, "error": "Invalid Argument: channel_id must be a non-empty string."})

        if not isinstance(sent_at, str) or not sent_at.strip():
            return json.dumps({"success": False, "error": "Invalid Argument: sent_at must be a non-empty string timestamp."})

        if not isinstance(emoji, str) or not emoji.strip():
            return json.dumps({"success": False, "error": "Invalid Argument: emoji must be a non-empty string."})

        if not isinstance(user_id, str) or not user_id.strip():
            return json.dumps({"success": False, "error": "Invalid Argument: user_id must be a non-empty string."})

        if thread_id is not None and (not isinstance(thread_id, str) or not thread_id.strip()):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: thread_id must be a non-empty string when provided."
            })

        if require_membership is None:
            require_membership = True

        if not isinstance(require_membership, bool):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: require_membership must be a boolean."
            })

        channels = data.get("channels", {})
        channel_members = data.get("channel_members", {})
        channel_messages = data.get("channel_messages", {})
        users = data.get("users", {})

        if not isinstance(channels, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'channels' must be a dictionary"})

        if not isinstance(channel_members, (dict, list)):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'channel_members' must be a dictionary or list"
            })

        if not isinstance(channel_messages, (dict, list)):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'channel_messages' must be a dictionary or list"
            })

        if not isinstance(users, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'users' must be a dictionary"})

        cid = str(channel_id).strip()
        uid = str(user_id).strip()
        ts = str(sent_at).strip()

        if uid not in users:
            return json.dumps({
                "success": False,
                "error": f"Authorization Error: user_id '{user_id}' not found."
            })

        if cid not in channels:
            return json.dumps({
                "success": False,
                "error": f"Foreign Key Error: channel_id '{channel_id}' not found."
            })

        channel_obj = channels.get(cid, {})
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
            if (cid, uid) not in pairs:
                return json.dumps({
                    "success": False,
                    "error": f"Authorization Error: user_id '{user_id}' is not a member of channel '{channel_id}'."
                })

        matches = []

        if isinstance(channel_messages, dict):
            for k, msg in channel_messages.items():
                if not isinstance(msg, dict):
                    continue
                if str(msg.get("channel_id", "")).strip() != cid:
                    continue
                if str(msg.get("sent_at", "")).strip() != ts:
                    continue
                if thread_id is not None and str(msg.get("thread_id", "")).strip() != str(thread_id).strip():
                    continue

                mid_raw = msg.get("message_id")
                mid_str = str(mid_raw).strip() if mid_raw is not None else str(k).strip()
                if not mid_str:
                    mid_str = str(k).strip()

                is_non_numeric = 1
                mid_int = 0
                try:
                    mid_int = int(mid_str)
                    is_non_numeric = 0
                except Exception:
                    is_non_numeric = 1
                    mid_int = 0

                matches.append({
                    "msg": msg,
                    "msg_key": str(k),
                    "mid_str": mid_str,
                    "is_non_numeric": is_non_numeric,
                    "mid_int": mid_int,
                })

        if isinstance(channel_messages, list):
            idx = 0
            for msg in channel_messages:
                idx += 1
                if not isinstance(msg, dict):
                    continue
                if str(msg.get("channel_id", "")).strip() != cid:
                    continue
                if str(msg.get("sent_at", "")).strip() != ts:
                    continue
                if thread_id is not None and str(msg.get("thread_id", "")).strip() != str(thread_id).strip():
                    continue

                mid_raw = msg.get("message_id")
                mid_str = str(mid_raw).strip() if mid_raw is not None else ""
                if not mid_str:
                    mid_str = str(idx)

                is_non_numeric = 1
                mid_int = 0
                try:
                    mid_int = int(mid_str)
                    is_non_numeric = 0
                except Exception:
                    is_non_numeric = 1
                    mid_int = 0

                matches.append({
                    "msg": msg,
                    "msg_key": str(idx),
                    "mid_str": mid_str,
                    "is_non_numeric": is_non_numeric,
                    "mid_int": mid_int,
                })

        if not matches:
            return json.dumps({
                "success": False,
                "error": (
                    f"Not Found Error: No message found for channel_id '{channel_id}' "
                    f"at timestamp '{sent_at}'."
                )
            })

        matches.sort(key=lambda r: (r["is_non_numeric"], r["mid_int"], r["mid_str"], r["msg_key"]))
        selected = matches[0]
        msg_obj = selected["msg"]

        message_id = str(msg_obj.get("message_id", "")).strip()
        if not message_id:
            message_id = str(selected.get("mid_str", "")).strip()
        if not message_id:
            message_id = str(selected.get("msg_key", "")).strip()

        emoji_norm = emoji.strip()
        if emoji_norm.startswith(":") and emoji_norm.endswith(":") and len(emoji_norm) > 2:
            emoji_norm = emoji_norm[1:-1]
        emoji_norm = emoji_norm.strip().lower()

        if not emoji_norm:
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: emoji must be a valid non-empty emoji name."
            })

        timestamp = "2026-02-02 23:59:00"

        reactions = msg_obj.get("reactions")
        if reactions is None:
            reactions = []
            msg_obj["reactions"] = reactions

        if not isinstance(reactions, list):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: message reactions must be a list."
            })

        existing_indexes = []
        idx2 = 0
        for r in reactions:
            idx2 += 1
            if not isinstance(r, dict):
                continue
            if str(r.get("emoji", "")).strip().lower() != emoji_norm:
                continue
            if str(r.get("user_id", "")).strip() != uid:
                continue
            existing_indexes.append(idx2 - 1)

        if action_norm == "add":
            if existing_indexes:
                if "updated_at" in msg_obj:
                    msg_obj["updated_at"] = timestamp
                return json.dumps({
                    "success": True,
                    "action": "add",
                    "added": False,
                    "already_exists": True,
                    "channel_id": cid,
                    "sent_at": ts,
                    "message_id": message_id,
                    "emoji": emoji_norm,
                    "user_id": uid,
                    "reactions": msg_obj.get("reactions", []),
                    "message": "Reaction already exists on the target message."
                })

            reactions.append({
                "emoji": emoji_norm,
                "user_id": uid,
                "created_at": timestamp
            })

            if "updated_at" in msg_obj:
                msg_obj["updated_at"] = timestamp

            return json.dumps({
                "success": True,
                "action": "add",
                "added": True,
                "channel_id": cid,
                "sent_at": ts,
                "message_id": message_id,
                "emoji": emoji_norm,
                "user_id": uid,
                "reactions": msg_obj.get("reactions", []),
                "message": "Reaction added successfully."
            })

        if not existing_indexes:
            if "updated_at" in msg_obj:
                msg_obj["updated_at"] = timestamp
            return json.dumps({
                "success": True,
                "action": "remove",
                "removed": False,
                "removed_count": 0,
                "channel_id": cid,
                "sent_at": ts,
                "message_id": message_id,
                "emoji": emoji_norm,
                "user_id": uid,
                "reactions": msg_obj.get("reactions", []),
                "message": "No matching reaction found to remove."
            })

        new_reactions = []
        removed_count = 0

        for r in reactions:
            if not isinstance(r, dict):
                new_reactions.append(r)
                continue
            if str(r.get("emoji", "")).strip().lower() == emoji_norm and str(r.get("user_id", "")).strip() == uid:
                removed_count += 1
                continue
            new_reactions.append(r)

        msg_obj["reactions"] = new_reactions

        if "updated_at" in msg_obj:
            msg_obj["updated_at"] = timestamp

        return json.dumps({
            "success": True,
            "action": "remove",
            "removed": True,
            "removed_count": removed_count,
            "channel_id": cid,
            "sent_at": ts,
            "message_id": message_id,
            "emoji": emoji_norm,
            "user_id": uid,
            "reactions": msg_obj.get("reactions", []),
            "message": "Reaction removed successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "manage_reaction",
                "description": (

                    "Modifies emoji reactions on a stored Slack message to reflect lightweight interaction signals such as acknowledgement, triage markers, or status indicators."

                    "PURPOSE: Manages the state of emoji reactions on specific messages to provide deterministic visual signals and maintain an accurate conversation record for downstream automation."

                    "WHEN TO USE: When a workflow needs to add or remove a reaction (like an approval checkmark or an 'eyes' emoji for triage) to a message, ensuring no duplicates are created and the reaction state remains synchronized with the current process status."

                    "RETURNS: A confirmation of whether the reaction was added or removed, the prior state of the reaction, and the updated list of reactions currently stored on the message record."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["add", "remove"],
                            "description": "Reaction modification action."
                        },
                        "channel_id": {
                            "type": "string",
                            "description": "Slack channel identifier containing the target message."
                        },
                        "sent_at": {
                            "type": "string",
                            "description": "Exact timestamp of the target message."
                        },
                        "emoji": {
                            "type": "string",
                            "description": "Emoji reaction name to add or remove."
                        },
                        "user_id": {
                            "type": "string",
                            "description": "Slack user identifier associated with the reaction."
                        },
                        "thread_id": {
                            "type": "string",
                            "description": "Slack thread identifier used to disambiguate threaded messages (optional )"
                        },
                        "require_membership": {
                            "type": "boolean",
                            "description": "Enforce membership checks for private or direct channels (optional )"
                        }
                    },
                    "required": ["action", "channel_id", "sent_at", "emoji", "user_id"]
                }
            }
        }
