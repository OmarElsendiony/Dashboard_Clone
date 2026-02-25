import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ModifyIncident(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        incident_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        project_id: Optional[str] = None,
        work_item_id: Optional[str] = None,
        service_id: Optional[str] = None,
        page_id: Optional[str] = None,
        acknowledged_at: Optional[str] = None,
        resolved_at: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format for incidents"}
            )

        if incident_id is None:
            return json.dumps({"success": False, "error": "incident_id is required"})

        incidents = data.get("incidents", {})

        incident = None
        incident_key_str = str(incident_id)

        if incident_key_str in incidents:
            incident_data = incidents[incident_key_str]
            if str(incident_data.get("incident_id")) == str(incident_id):
                incident = incident_data

        if not incident:
            for _incident_key, incident_data in incidents.items():
                if str(incident_data.get("incident_id")) == str(incident_id):
                    incident = incident_data
                    break

        if not incident:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Incident with ID {str(incident_id)} not found",
                }
            )

        # Validate project_id exists if being updated
        if project_id is not None:
            projects = data.get("projects", {})
            project = None
            project_key_str = str(project_id)

            if project_key_str in projects:
                project_data = projects[project_key_str]
                if str(project_data.get("project_id")) == str(project_id):
                    project = project_data

            if not project:
                for project_data in projects.values():
                    if str(project_data.get("project_id")) == str(project_id):
                        project = project_data
                        break

            if not project:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Project with ID {str(project_id)} not found",
                    }
                )

        # Validate work_item_id exists if being updated
        if work_item_id is not None:
            work_items = data.get("work_items", {})
            work_item_exists = False

            for _work_item_key, work_item_data in work_items.items():
                if str(work_item_data.get("work_item_id")) == str(work_item_id):
                    work_item_exists = True
                    break

            if not work_item_exists:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Work item with ID {str(work_item_id)} not found",
                    }
                )

        # Validate service_id exists if being updated
        if service_id is not None:
            services = data.get("services", {})
            service_exists = False

            for _service_key, service_data in services.items():
                if str(service_data.get("service_id")) == str(service_id):
                    service_exists = True
                    break

            if not service_exists:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Service with ID {str(service_id)} not found",
                    }
                )

        # Validate page_id exists if being updated
        if page_id is not None:
            pages = data.get("pages", {})
            page_exists = False

            for _page_key, page_data in pages.items():
                if str(page_data.get("page_id")) == str(page_id):
                    page_exists = True
                    break

            if not page_exists:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Page with ID {str(page_id)} not found",
                    }
                )

        if status is not None:
            valid_statuses = [
                "open",
                "in_progress",
                "acknowledged",
                "closed",
                "resolved",
            ]
            if status not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}",
                    }
                )

        if severity is not None:
            valid_severities = ["low", "medium", "high", "critical"]
            if severity not in valid_severities:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid severity '{severity}'. Must be one of: {', '.join(valid_severities)}",
                    }
                )

        if (
            title is None
            and description is None
            and status is None
            and severity is None
            and project_id is None
            and work_item_id is None
            and service_id is None
            and page_id is None
            and acknowledged_at is None
            and resolved_at is None
        ):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one field must be provided for update",
                }
            )

        # Update fields
        if title is not None:
            title_str = str(title)
            if len(title_str) > 500:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Title exceeds maximum length of 500 characters (current length: {len(title_str)})",
                    }
                )
            incident["title"] = title_str

        if description is not None:
            incident["description"] = str(description) if description else None

        if status is not None:
            incident["status"] = str(status)
            # Handle lifecycle timestamps based on status transitions
            if status == "acknowledged" and not incident.get("acknowledged_at"):
                incident["acknowledged_at"] = "2026-02-11T23:59:00"
            if status in ["resolved", "closed"] and not incident.get("resolved_at"):
                incident["resolved_at"] = "2026-02-11T23:59:00"

        if severity is not None:
            incident["severity"] = str(severity)

        if project_id is not None:
            incident["project_id"] = str(project_id)

        if work_item_id is not None:
            incident["work_item_id"] = str(work_item_id)

        if service_id is not None:
            incident["service_id"] = str(service_id)

        if page_id is not None:
            incident["page_id"] = str(page_id)

        if acknowledged_at is not None:
            incident["acknowledged_at"] = (
                str(acknowledged_at) if acknowledged_at else None
            )

        if resolved_at is not None:
            incident["resolved_at"] = str(resolved_at) if resolved_at else None

        incident["updated_at"] = "2026-02-11T23:59:00"

        updated_incident = incident.copy()
        # Ensure all fields are strings
        if updated_incident.get("incident_id") is not None:
            updated_incident["incident_id"] = str(updated_incident.get("incident_id"))
        if updated_incident.get("project_id") is not None:
            updated_incident["project_id"] = str(updated_incident.get("project_id"))
        if updated_incident.get("work_item_id") is not None:
            updated_incident["work_item_id"] = str(updated_incident.get("work_item_id"))
        if updated_incident.get("service_id") is not None:
            updated_incident["service_id"] = str(updated_incident.get("service_id"))
        if updated_incident.get("page_id") is not None:
            updated_incident["page_id"] = str(updated_incident.get("page_id"))
        if updated_incident.get("status") is not None:
            updated_incident["status"] = str(updated_incident.get("status"))
        if updated_incident.get("severity") is not None:
            updated_incident["severity"] = str(updated_incident.get("severity"))
        if updated_incident.get("title") is not None:
            updated_incident["title"] = str(updated_incident.get("title"))
        if updated_incident.get("description") is not None:
            updated_incident["description"] = str(updated_incident.get("description"))
        if updated_incident.get("created_at") is not None:
            updated_incident["created_at"] = str(updated_incident.get("created_at"))
        if updated_incident.get("updated_at") is not None:
            updated_incident["updated_at"] = str(updated_incident.get("updated_at"))
        if updated_incident.get("acknowledged_at") is not None:
            updated_incident["acknowledged_at"] = str(
                updated_incident.get("acknowledged_at")
            )
        if updated_incident.get("resolved_at") is not None:
            updated_incident["resolved_at"] = str(updated_incident.get("resolved_at"))

        return json.dumps(
            {
                "success": True,
                "incident": updated_incident,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "modify_incident",
                "description": "Update incident information. Can update title, description, status, severity, project, work item, service, page, and timestamps. Automatically sets lifecycle timestamps (acknowledged_at, resolved_at) based on status transitions. Use this to manage incident lifecycle, update incident details, and link incidents to projects and work items.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "incident_id": {
                            "type": "string",
                            "description": "The incident ID to update",
                        },
                        "title": {
                            "type": "string",
                            "description": "New title for the incident",
                        },
                        "description": {
                            "type": "string",
                            "description": "New description for the incident",
                        },
                        "status": {
                            "type": "string",
                            "description": "New status for the incident",
                            "enum": [
                                "open",
                                "in_progress",
                                "acknowledged",
                                "closed",
                                "resolved",
                            ],
                        },
                        "severity": {
                            "type": "string",
                            "description": "New severity level for the incident",
                            "enum": ["low", "medium", "high", "critical"],
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project ID to associate the incident with",
                        },
                        "work_item_id": {
                            "type": "string",
                            "description": "Work item ID to link the incident to",
                        },
                        "service_id": {
                            "type": "string",
                            "description": "Service ID associated with the incident",
                        },
                        "page_id": {
                            "type": "string",
                            "description": "Page ID associated with the incident",
                        },
                        "acknowledged_at": {
                            "type": "string",
                            "description": "Timestamp when incident was acknowledged (ISO format: YYYY-MM-DDTHH:MM:SS)",
                        },
                        "resolved_at": {
                            "type": "string",
                            "description": "Timestamp when incident was resolved (ISO format: YYYY-MM-DDTHH:MM:SS)",
                        },
                    },
                    "required": ["incident_id"],
                },
            },
        }
