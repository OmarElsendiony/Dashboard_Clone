import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class GetIncidents(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        incident_id: Optional[str] = None,
        title: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        project_id: Optional[str] = None,
        issue_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not any([incident_id, title, severity, status, project_id, issue_id]):
            return json.dumps({
                "success": False,
                "error": "At least one filter parameter must be provided",
            })

        if severity is not None:
            severity_str = str(severity).strip()
            valid_severities = ["low", "medium", "high", "critical"]
            if severity_str not in valid_severities:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid severity '{severity_str}'. Valid values: {', '.join(valid_severities)}",
                    }
                )
        else:
            severity_str = None

        if status is not None:
            status_str = str(status).strip()
            valid_statuses = ["open", "acknowledged", "in_progress", "resolved", "closed"]
            if status_str not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status '{status_str}'. Valid values: {', '.join(valid_statuses)}",
                    }
                )
        else:
            status_str = None

        incident_id_str = str(incident_id).strip() if incident_id else None
        title_str = str(title).strip() if title else None
        project_id_str = str(project_id).strip() if project_id else None
        issue_id_str = str(issue_id).strip() if issue_id else None

        incidents = data.get("incidents", {})
        projects = data.get("projects", {})
        work_items = data.get("work_items", {})

        if project_id_str is not None and project_id_str not in projects:
            return json.dumps({"success": False, "error": f"Project '{project_id_str}' not found"})

        if issue_id_str is not None and issue_id_str not in work_items:
            return json.dumps({"success": False, "error": f"Issue '{issue_id_str}' not found"})

        results = []
        for incident in incidents.values():
            if incident_id_str is not None and str(incident.get("incident_id", "")) != incident_id_str:
                continue

            if title_str is not None and title_str.lower() != str(incident.get("title", "")).lower():
                continue

            if severity_str is not None and str(incident.get("severity", "")) != severity_str:
                continue

            if status_str is not None and str(incident.get("status", "")) != status_str:
                continue

            if project_id_str is not None and str(incident.get("project_id", "")) != project_id_str:
                continue

            if issue_id_str is not None:
                inc_wid = incident.get("work_item_id")
                if inc_wid is None or str(inc_wid) != issue_id_str:
                    continue

            filtered_incident = {
                "incident_id": str(incident.get("incident_id", "")),
                "title": str(incident.get("title", "")),
                "description": str(incident.get("description", "")) if incident.get("description") else None,
                "severity": str(incident.get("severity", "")),
                "status": str(incident.get("status", "")),
                "project_id": str(incident.get("project_id", "")) if incident.get("project_id") else None,
                "issue_id": str(incident.get("work_item_id", "")) if incident.get("work_item_id") else None,
                "created_at": str(incident.get("created_at", "")),
                "updated_at": str(incident.get("updated_at", "")),
            }
            results.append(filtered_incident)
        results.sort(key=lambda x: int(x["incident_id"]))
        return json.dumps({"success": True, "incidents": results, "count": int(len(results))})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_incidents",
                "description": "Retrieves incident records based on optional filter criteria.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "incident_id": {
                            "type": "string",
                            "description": "Filter by the exact unique incident identifier (incident_id).",
                        },
                        "title": {
                            "type": "string",
                            "description": "Filter by incident title (exact, case-insensitive).",
                        },
                        "severity": {
                            "type": "string",
                            "description": "Filter by incident severity",
                            "enum": ["low", "medium", "high", "critical"],
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by incident status",
                            "enum": ["open", "acknowledged", "in_progress", "resolved", "closed"],
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Filter by the project identifier (project_id).",
                        },
                        "issue_id": {
                            "type": "string",
                            "description": "Filter by the linked issue identifier (issue_id).",
                        },
                    },
                    "anyOf": [
                        {"required": ["incident_id"]},
                        {"required": ["title"]},
                        {"required": ["severity"]},
                        {"required": ["status"]},
                        {"required": ["project_id"]},
                        {"required": ["issue_id"]},
                    ],
                    "required": [],
                },
            },
        }
