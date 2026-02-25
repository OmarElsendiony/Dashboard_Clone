import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class UpdateChannel(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_identifier: Dict[str, str],
        applied_updates: Dict[str, Any],
    ) -> str:
        # 1. Basic data integrity check
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not isinstance(channel_identifier, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "channel_identifier must be a dictionary object.",
                }
            )

        if not isinstance(applied_updates, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "applied_updates must be a dictionary object.",
                }
            )

        # Validate exactly one key provided for channel_identifier
        channel_keys = [
            k for k in ["channel_id", "channel_name"] if channel_identifier.get(k)
        ]
        if len(channel_keys) != 1:
            return json.dumps(
                {
                    "success": False,
                    "error": "Exactly one identifier key required for channel_identifier (channel_id or channel_name).",
                }
            )

        if not applied_updates:
            return json.dumps(
                {"success": False, "error": "applied_updates cannot be empty."}
            )

        # System Epoch: 2026-02-11T23:59:00
        now = "2026-02-11T23:59:00"
        channels = data.get("channels", {})
        projects = data.get("projects", {})
        incidents = data.get("incidents", {})

        # 2. Flexible Identification Logic via channel_identifier
        target_channel = None
        c_id = channel_identifier.get("channel_id")
        c_name = channel_identifier.get("channel_name")

        # Validate channel_name length if provided
        if c_name and len(c_name) > 255:
            return json.dumps(
                {
                    "success": False,
                    "error": "Channel name in identifier exceeds maximum length of 255 characters.",
                }
            )

        if c_id:
            target_channel = channels.get(c_id) or channels.get(str(c_id))
        elif c_name:
            lookup_name = c_name.lower().replace(" ", "-")
            if not lookup_name.startswith("channel-"):
                lookup_name = f"channel-{lookup_name}"
            target_channel = next(
                (c for c in channels.values() if c["channel_name"] == lookup_name or c["channel_name"] == c_name), None
            )

        if not target_channel:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Channel identified by {channel_identifier} not found.",
                }
            )

        # 3. Extract and Validate Updates
        status = applied_updates.get("status")
        description = applied_updates.get("description")

        # Validation: Status Enum and Governance State Check
        if status:
            valid_statuses = ["active", "archived"]
            if status not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status. Must be one of {valid_statuses}",
                    }
                )

            if target_channel["status"] == status:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"No status change. Current status is already {status}",
                    }
                )

            # Integrity Guard: Archival requires closed parent entities
            if status == "archived":
                # Check associated project
                p_id = target_channel.get("project_id")
                if p_id and p_id in projects:
                    if projects[p_id].get("status") != "closed":
                        return json.dumps(
                            {
                                "success": False,
                                "error": "Cannot archive channel: Associated project is still active.",
                            }
                        )

                # Check associated incident
                i_id = target_channel.get("incident_id")
                if i_id and i_id in incidents:
                    if incidents[i_id].get("status") not in ["resolved", "closed"]:
                        return json.dumps(
                            {
                                "success": False,
                                "error": "Cannot archive channel: Associated incident is not resolved.",
                            }
                        )

            target_channel["status"] = status

        # 4. Update Description
        if description:
            if description != target_channel.get("description"):
                target_channel["description"] = description
            else:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Description update failed. Content is identical to existing description.",
                    }
                )

        target_channel["updated_at"] = now

        return json.dumps(
            {
                "success": True,
                "message": f"Channel '{target_channel['channel_name']}' updated successfully.",
                "channel": target_channel,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_channel",
                "description": "Modifies communication hub metadata or lifecycle states. Archiving a channel is only permitted if the associated project or incident is in a closed or resolved state.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_identifier": {
                            "type": "object",
                            "description": "Lookup dictionary (id or name) for the target channel.",
                            "properties": {
                                "channel_id": {
                                    "type": "string",
                                    "description": "Unique ID for the channel.",
                                },
                                "channel_name": {
                                    "type": "string",
                                    "maxLength": 255,
                                    "description": "Formal handle for the channel (max 255 characters).",
                                },
                            },
                            "additionalProperties": False,
                        },
                        "applied_updates": {
                            "type": "object",
                            "description": "Fields to modify.",
                            "properties": {
                                "status": {
                                    "type": "string",
                                    "enum": ["active", "archived"],
                                    "description": "The new state. 'archived' requires parent entity closure.",
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Revised intent of the channel.",
                                },
                            },
                            "additionalProperties": False,
                        },
                    },
                    "required": ["channel_identifier", "applied_updates"],
                },
            },
        }
