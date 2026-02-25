import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class InitiateChannel(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_name: str,
        channel_type: str,
        description: Optional[str] = None,
        project_identifier: Optional[Dict[str, str]] = None,
        incident_identifier: Optional[Dict[str, str]] = None,
        work_item_identifier: Optional[Dict[str, str]] = None,
    ) -> str:
        # 1. Basic data integrity check
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        # Validate identifier types
        if project_identifier is not None and not isinstance(project_identifier, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "project_identifier must be a dictionary object.",
                }
            )

        if incident_identifier is not None and not isinstance(
            incident_identifier, dict
        ):
            return json.dumps(
                {
                    "success": False,
                    "error": "incident_identifier must be a dictionary object.",
                }
            )

        if work_item_identifier is not None and not isinstance(
            work_item_identifier, dict
        ):
            return json.dumps(
                {
                    "success": False,
                    "error": "work_item_identifier must be a dictionary object.",
                }
            )

        # System Epoch: 2026-02-11T23:59:00
        now = "2026-02-11T23:59:00"

        channels = data.get("channels", {})
        projects = data.get("projects", {})
        incidents = data.get("incidents", {})
        work_items = data.get("work_items", {})

        def generate_id(table: Dict[str, Any]) -> str:
            return str(max([int(k) for k in table.keys()], default=0) + 1)

        # Validation: Channel name length
        if len(channel_name) > 255:
            return json.dumps(
                {
                    "success": False,
                    "error": "Channel name exceeds maximum length of 255 characters.",
                }
            )

        # Validation: Channel type enum
        valid_channel_types = ["room", "dm"]
        if channel_type not in valid_channel_types:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid channel_type '{channel_type}'. Must be one of: {', '.join(valid_channel_types)}",
                }
            )

        # Validation: Exactly one entity linkage required
        entity_count = sum(
            [
                1 if project_identifier else 0,
                1 if incident_identifier else 0,
                1 if work_item_identifier else 0,
            ]
        )
        if entity_count == 0:
            return json.dumps(
                {
                    "success": False,
                    "error": "Channel must be linked to exactly one entity: Project, Incident, or Work Item.",
                }
            )
        if entity_count > 1:
            return json.dumps(
                {
                    "success": False,
                    "error": "Channel can only be linked to exactly one entity. Provide only one of: project_identifier, incident_identifier, or work_item_identifier.",
                }
            )

        # Validation: Naming Convention Enforcement
        formatted_name = channel_name.lower().replace(" ", "-")
        if not formatted_name.startswith("channel-"):
            formatted_name = f"channel-{formatted_name}"

        # Idempotency Check: Verify channel_name uniqueness
        if any(c["channel_name"] == formatted_name for c in channels.values()):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Channel '{formatted_name}' already exists.",
                }
            )

        # 4. Verification: Associated Project
        target_project_id = None
        if project_identifier:
            p_id = project_identifier.get("project_id")
            p_name = project_identifier.get("project_name")
            p_key = project_identifier.get("project_key")

            if p_id:
                target_project_id = p_id
            elif p_name:
                target_project_id = next(
                    (k for k, v in projects.items() if v["project_name"] == p_name),
                    None,
                )
            elif p_key:
                target_project_id = next(
                    (k for k, v in projects.items() if v["project_key"] == p_key), None
                )

            if not target_project_id or target_project_id not in projects:
                return json.dumps(
                    {"success": False, "error": "Linked project not found."}
                )
            if projects[target_project_id].get("status") == "closed":
                return json.dumps(
                    {
                        "success": False,
                        "error": "Cannot link channel to a closed project.",
                    }
                )

        # 5. Verification: Associated Incident
        target_incident_id = None
        if incident_identifier:
            i_id = incident_identifier.get("incident_id")
            i_title = incident_identifier.get("title")

            if i_id:
                target_incident_id = i_id
            elif i_title:
                target_incident_id = next(
                    (k for k, v in incidents.items() if v["title"] == i_title), None
                )

            if not target_incident_id or target_incident_id not in incidents:
                return json.dumps(
                    {"success": False, "error": "Linked incident not found."}
                )

        # 6. Verification: Associated Work Item
        target_work_item_id = None
        if work_item_identifier:
            w_id = work_item_identifier.get("work_item_id")
            w_title = work_item_identifier.get("title")

            if w_id:
                target_work_item_id = w_id
            elif w_title:
                target_work_item_id = next(
                    (k for k, v in work_items.items() if v["title"] == w_title), None
                )

            if not target_work_item_id or target_work_item_id not in work_items:
                return json.dumps(
                    {"success": False, "error": "Linked work item not found."}
                )

        # 7. Execution: Provision
        new_id = generate_id(channels)
        new_channel = {
            "channel_id": new_id,
            "channel_name": formatted_name,
            "description": description or f"Collaboration hub for {formatted_name}",
            "channel_type": channel_type,
            "status": "active",
            "project_id": target_project_id,
            "incident_id": target_incident_id,
            "work_item_id": target_work_item_id,
            "created_at": now,
            "updated_at": now,
        }
        channels[new_id] = new_channel

        return json.dumps({"success": True, "channel": new_channel})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "initiate_channel",
                "description": "Provisions a new communication hub while verifying that the associated project is not closed and that linked incidents or work items exist in the system registry.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_name": {
                            "type": "string",
                            "maxLength": 255,
                            "description": "The requested name for the channel (max 255 characters). Automatically formatted with 'channel-' prefix.",
                        },
                        "description": {
                            "type": "string",
                            "description": "A summary of the channel's specific collaboration intent.",
                        },
                        "channel_type": {
                            "type": "string",
                            "enum": ["room", "dm"],
                            "default": "room",
                            "description": "The category of the space (e.g., public room or direct message).",
                        },
                        "project_identifier": {
                            "type": "object",
                            "description": "A lookup dictionary to link the channel to an existing project.",
                            "properties": {
                                "project_id": {
                                    "type": "string",
                                    "description": "The unique ID of the project.",
                                },
                                "project_name": {
                                    "type": "string",
                                    "description": "The formal name of the project (e.g., 'Project Titan').",
                                },
                                "project_key": {
                                    "type": "string",
                                    "description": "The technical project key.",
                                },
                            },
                            "OneOf": ["project_id", "project_name", "project_key"],
                        },
                        "incident_identifier": {
                            "type": "object",
                            "description": "A lookup dictionary to link the channel to a specific incident.",
                            "properties": {
                                "incident_id": {
                                    "type": "string",
                                    "description": "The unique system ID for the incident.",
                                },
                                "title": {
                                    "type": "string",
                                    "description": "The formal title of the incident report used for lookup.",
                                },
                            },
                            "OneOf": ["incident_id", "title"],
                        },
                        "work_item_identifier": {
                            "type": "object",
                            "description": "A lookup dictionary to link the channel to a specific work item or task.",
                            "properties": {
                                "work_item_id": {
                                    "type": "string",
                                    "description": "The unique system ID for the work item.",
                                },
                                "title": {
                                    "type": "string",
                                    "description": "The exact title of the work item used to identify the record.",
                                },
                            },
                            "OneOf": ["incident_id", "title"],
                        },
                    },
                    "required": ["channel_name", "channel_type"],
                },
            },
        }
