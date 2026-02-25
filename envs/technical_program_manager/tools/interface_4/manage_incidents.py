import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class ManageIncidents(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        action: str,
        incident_id: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        project_id: Optional[str] = None,
        issue_id: Optional[str] = None,
    ) -> str:
        timestamp = "2026-02-11T23:59:00"

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        action_str = str(action).strip().lower()
        valid_actions = ["create", "update", "delete"]
        if action_str not in valid_actions:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid action '{action_str}'. Valid values: {', '.join(valid_actions)}",
                }
            )

        incidents = data.get("incidents", {})
        projects = data.get("projects", {})
        work_items = data.get("work_items", {})
        valid_severities = ["low", "medium", "high", "critical"]
        valid_statuses = ["open", "acknowledged", "in_progress", "resolved", "closed"]

        if action_str == "create":
            if incident_id is not None:
                return json.dumps(
                    {
                        "success": False,
                        "error": "incident_id should not be provided when creating an incident",
                    }
                )

            if not title:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Create requires: title",
                    }
                )

            if not project_id:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Create requires: project_id",
                    }
                )

            title_str = str(title).strip()
            pid = str(project_id).strip()

            # Validate project exists
            if pid not in projects:
                return json.dumps({"success": False, "error": f"Project '{pid}' not found"})

            if severity is not None:
                severity_str = str(severity).strip()
                if severity_str not in valid_severities:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Invalid severity '{severity_str}'. Valid values: {', '.join(valid_severities)}",
                        }
                    )
            else:
                severity_str = "medium"

            if status is not None:
                status_str = str(status).strip()
                if status_str not in valid_statuses:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Invalid status '{status_str}'. Valid values: {', '.join(valid_statuses)}",
                        }
                    )
            else:
                status_str = "open"

            # Duplicate title check within project
            for inc in incidents.values():
                if (str(inc.get("project_id", "")) == pid
                        and str(inc.get("title", "")).lower() == title_str.lower()):
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Incident with title '{title_str}' already exists in project '{pid}'",
                        }
                    )

            # Validate issue_id if provided — must exist and belong to same project
            work_item_id = None
            if issue_id is not None:
                iid = str(issue_id).strip()
                wi = work_items.get(iid)
                if wi is None:
                    return json.dumps({"success": False, "error": f"Issue '{iid}' not found"})
                if str(wi.get("project_id", "")) != pid:
                    return json.dumps({"success": False, "error": f"Issue '{iid}' does not belong to project '{pid}'"})
                work_item_id = iid

            if incidents:
                max_id = max(int(k) for k in incidents.keys())
                new_id = str(max_id + 1)
            else:
                new_id = "1"

            new_incident = {
                "incident_id": new_id,
                "title": title_str,
                "description": str(description).strip() if description else None,
                "severity": severity_str,
                "status": status_str,
                "project_id": pid,
                "work_item_id": work_item_id,
                "created_at": timestamp,
                "updated_at": timestamp,
            }

            incidents[new_id] = new_incident

            response = {
                "incident_id": str(new_incident.get("incident_id", "")),
                "title": str(new_incident.get("title", "")),
                "description": str(new_incident.get("description", "")) if new_incident.get("description") else None,
                "severity": str(new_incident.get("severity", "")) if new_incident.get("severity") else None,
                "status": str(new_incident.get("status", "")),
                "project_id": str(new_incident.get("project_id", "")) if new_incident.get("project_id") else None,
                "issue_id": str(new_incident.get("work_item_id", "")) if new_incident.get("work_item_id") else None,
                "created_at": str(new_incident.get("created_at", "")),
                "updated_at": str(new_incident.get("updated_at", "")),
            }
            return json.dumps({"success": True, "incident": response})

        elif action_str == "update":
            if not incident_id:
                return json.dumps(
                    {"success": False, "error": "Update requires: incident_id"}
                )

            iid = str(incident_id).strip()
            incident = incidents.get(iid)
            if incident is None:
                return json.dumps(
                    {"success": False, "error": f"Incident '{iid}' not found"}
                )

            # Restrict update to description, severity, status only
            if not any([description, severity, status]):
                return json.dumps(
                    {
                        "success": False,
                        "error": "At least one field to update must be provided (description, severity, status)",
                    }
                )

            # Block non-status field updates on resolved/closed incidents
            current_status = str(incident.get("status", ""))
            if current_status in ["resolved", "closed"]:
                if description is not None or severity is not None:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Cannot update incident with status '{current_status}'. Incident must not be 'resolved' or 'closed'.",
                        }
                    )

            if description is not None:
                incident["description"] = str(description).strip()

            if severity is not None:
                severity_val = str(severity).strip()
                if severity_val not in valid_severities:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Invalid severity '{severity_val}'. Valid values: {', '.join(valid_severities)}",
                        }
                    )
                incident["severity"] = severity_val

            if status is not None:
                status_val = str(status).strip()
                if status_val not in valid_statuses:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Invalid status '{status_val}'. Valid values: {', '.join(valid_statuses)}",
                        }
                    )
                # Enforce status transition rules
                valid_transitions = {
                    "open": ["acknowledged"],
                    "acknowledged": ["in_progress", "resolved"],
                    "in_progress": ["resolved"],
                    "resolved": ["closed"],
                    "closed": [],
                }
                allowed = valid_transitions.get(current_status, [])
                if status_val not in allowed:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Invalid status transition from '{current_status}' to '{status_val}'. Allowed transitions: {', '.join(allowed) if allowed else 'none'}",
                        }
                    )
                incident["status"] = status_val

            incident["updated_at"] = timestamp

            response = {
                "incident_id": str(incident.get("incident_id", "")),
                "title": str(incident.get("title", "")),
                "description": str(incident.get("description", "")) if incident.get("description") else None,
                "severity": str(incident.get("severity", "")) if incident.get("severity") else None,
                "status": str(incident.get("status", "")),
                "project_id": str(incident.get("project_id", "")) if incident.get("project_id") else None,
                "issue_id": str(incident.get("work_item_id", "")) if incident.get("work_item_id") else None,
                "created_at": str(incident.get("created_at", "")),
                "updated_at": str(incident.get("updated_at", "")),
            }
            return json.dumps({"success": True, "incident": response})

        elif action_str == "delete":
            if not incident_id:
                return json.dumps(
                    {"success": False, "error": "Delete requires: incident_id"}
                )

            iid = str(incident_id).strip()
            if iid not in incidents:
                return json.dumps(
                    {"success": False, "error": f"Incident '{iid}' not found"}
                )

            incident = incidents[iid]

            # Only delete if status is "closed"
            inc_status = str(incident.get("status", ""))
            if inc_status != "closed":
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Cannot delete incident with status '{inc_status}'. Only incidents with status 'closed' can be deleted.",
                    }
                )

            # Clear incident_id on documents
            documents = data.get("documents", {})
            for doc in documents.values():
                if doc.get("incident_id") is not None and str(doc.get("incident_id", "")) == iid:
                    doc["incident_id"] = None

            deleted_incident = incidents.pop(iid)
            return json.dumps(
                {
                    "success": True,
                    "message": f"Incident '{str(deleted_incident.get('title', ''))}' has been deleted",
                }
            )

        return json.dumps({"success": False, "error": "Unexpected error"})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "manage_incidents",
                "description": "Manages incident lifecycle by creating, updating, or deleting incident records.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "The action to perform",
                            "enum": ["create", "update", "delete"],
                        },
                        "incident_id": {
                            "type": "string",
                            "description": "Unique incident identifier.",
                        },
                        "title": {
                            "type": "string",
                            "description": "Incident title",
                        },
                        "description": {
                            "type": "string",
                            "description": "Incident description",
                        },
                        "severity": {
                            "type": "string",
                            "description": "Incident severity. Default is 'medium'.",
                            "enum": ["low", "medium", "high", "critical"],
                        },
                        "status": {
                            "type": "string",
                            "description": "Incident status. Default is 'open'.",
                            "enum": ["open", "acknowledged", "in_progress", "resolved", "closed"],
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier (project_id).",
                        },
                        "issue_id": {
                            "type": "string",
                            "description": "Linked issue identifier (issue_id).",
                        },
                    },
                    "required": ["action"],
                    "allOf": [
                        {
                            "if": {
                                "properties": {"action": {"enum": ["create"]}}
                            },
                            "then": {
                                "required": ["title", "project_id"]
                            },
                        },
                        {
                            "if": {
                                "properties": {"action": {"enum": ["update"]}}
                            },
                            "then": {
                                "required": ["incident_id"],
                                "anyOf": [
                                    {"required": ["description"]},
                                    {"required": ["severity"]},
                                    {"required": ["status"]},
                                ],
                            },
                        },
                        {
                            "if": {
                                "properties": {"action": {"enum": ["delete"]}}
                            },
                            "then": {
                                "required": ["incident_id"]
                            },
                        },
                    ],
                },
            },
        }
