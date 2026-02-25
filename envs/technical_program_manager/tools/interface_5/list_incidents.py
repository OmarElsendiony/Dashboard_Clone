import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ListIncidents(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        incident_id: Optional[str] = None,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format for incidents"}
            )

        if all(param is None for param in [incident_id, project_id, status, severity]):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one filter parameter is required (incident_id, project_id, status, or severity)",
                }
            )

        incidents = data.get("incidents", {})

        if incident_id is not None:
            # If project_id is provided alongside incident_id, validate the project exists
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

            incident = None
            incident_key_str = str(incident_id)

            if incident_key_str in incidents:
                incident_data = incidents[incident_key_str]
                if str(incident_data.get("incident_id")) == str(incident_id):
                    incident = incident_data.copy()

            if not incident:
                for _incident_key, incident_data in incidents.items():
                    if str(incident_data.get("incident_id")) == str(incident_id):
                        incident = incident_data.copy()
                        break

            if not incident:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Incident with ID {str(incident_id)} not found",
                    }
                )

            if project_id is not None and str(incident.get("project_id")) != str(
                project_id
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Incident with ID {str(incident_id)} is not in project {str(project_id)}",
                    }
                )

            if status is not None and incident.get("status") != status:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Incident with ID {str(incident_id)} does not match status '{status}'",
                    }
                )

            if severity is not None and incident.get("severity") != severity:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Incident with ID {str(incident_id)} does not match severity '{severity}'",
                    }
                )

            # Explicit type casting for all fields
            incident["incident_id"] = str(incident.get("incident_id"))
            incident["project_id"] = str(incident.get("project_id"))
            incident["status"] = str(incident.get("status"))
            incident["severity"] = str(incident.get("severity"))
            incident["title"] = str(incident.get("title"))
            incident["description"] = str(incident.get("description"))
            incident["created_at"] = str(incident.get("created_at"))
            incident["updated_at"] = str(incident.get("updated_at"))

            return json.dumps(
                {
                    "success": True,
                    "incident": incident,
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

        results = []

        for _incident_key, incident in incidents.items():
            if project_id is not None:
                item_project_id = incident.get("project_id")
                if str(item_project_id) != str(project_id):
                    continue

            if status is not None:
                if incident.get("status") != status:
                    continue

            if severity is not None:
                if incident.get("severity") != severity:
                    continue

            incident_copy = incident.copy()
            # Explicit type casting for all fields
            incident_copy["incident_id"] = str(incident_copy.get("incident_id"))
            incident_copy["project_id"] = str(incident_copy.get("project_id"))
            incident_copy["status"] = str(incident_copy.get("status"))
            incident_copy["severity"] = str(incident_copy.get("severity"))
            incident_copy["title"] = str(incident_copy.get("title"))
            incident_copy["description"] = str(incident_copy.get("description"))
            incident_copy["created_at"] = str(incident_copy.get("created_at"))
            incident_copy["updated_at"] = str(incident_copy.get("updated_at"))

            results.append(incident_copy)

        return json.dumps(
            {
                "success": True,
                "count": len(results),
                "incidents": results,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_incidents",
                "description": "List and filter incidents. Requires at least one filter parameter (incident_id, project_id, status, or severity). Use this to track incident management, identify critical issues, and monitor incident status across projects.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "incident_id": {
                            "type": "string",
                            "description": "The incident ID to retrieve. If provided, returns that specific incident.",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Filter incidents by project ID",
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter incidents by status",
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
                            "description": "Filter incidents by severity level",
                            "enum": ["low", "medium", "high", "critical"],
                        },
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["incident_id"]},
                        {"required": ["project_id"]},
                        {"required": ["status"]},
                        {"required": ["severity"]},
                    ],
                },
            },
        }
