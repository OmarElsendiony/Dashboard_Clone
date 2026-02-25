import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetIncident(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        project_id: str,
        incident_number: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        if not project_id or not str(project_id).strip():
            return json.dumps(
                {
                    "success": False,
                    "error": "Missing required parameter: 'project_id'",
                }
            )

        project_id_str = str(project_id).strip()
        incident_number_str = str(incident_number).strip() if incident_number else None

        incidents_dict = data.get("incidents", {})
        projects_dict = data.get("projects", {})

        if project_id_str not in projects_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Project with ID '{project_id_str}' not found",
                }
            )

        if incident_number_str:
            found_incident = None
            for _, inc_data in incidents_dict.items():
                if not isinstance(inc_data, dict):
                    continue
                if (
                    str(inc_data.get("project_id", "")).strip() == project_id_str
                    and str(inc_data.get("incident_number", "")).strip()
                    == incident_number_str
                ):
                    found_incident = inc_data.copy()
                    break

            if not found_incident:
                return json.dumps(
                    {
                        "success": False,
                        "error": (
                            f"Incident with number '{incident_number_str}' not found "
                            f"in project '{project_id_str}'"
                        ),
                    }
                )

            found_incident["project_id"] = str(found_incident.get("project_id", ""))
            found_incident["incident_number"] = str(
                found_incident.get("incident_number", "")
            )
            found_incident["title"] = str(found_incident.get("title", ""))
            found_incident["description"] = str(found_incident.get("description", ""))
            found_incident["status"] = str(found_incident.get("status", ""))
            found_incident["severity"] = str(found_incident.get("severity", ""))
            found_incident["incident_id"] = str(found_incident.get("incident_id", ""))
            found_incident["work_item_id"] = str(found_incident.get("work_item_id", ""))
            found_incident["created_at"] = str(found_incident.get("created_at", ""))
            found_incident["updated_at"] = str(found_incident.get("updated_at", ""))
            found_incident["resolved_at"] = str(found_incident.get("resolved_at", ""))
            found_incident["acknowledged_at"] = str(
                found_incident.get("acknowledged_at", "")
            )
            found_incident.pop("service_id", None)
            found_incident.pop("page_id", None)

            return json.dumps(
                {
                    "success": True,
                    "incident": found_incident,
                    "message": (
                        f"Incident '{incident_number_str}' retrieved successfully "
                        f"from project '{project_id_str}'"
                    ),
                }
            )

        matching_incidents = []
        for _, inc_data in incidents_dict.items():
            if not isinstance(inc_data, dict):
                continue

            # Filter by project_id
            if str(inc_data.get("project_id", "")).strip() != project_id_str:
                continue

            found_incident = inc_data.copy()
            found_incident["project_id"] = str(found_incident.get("project_id", ""))
            found_incident["incident_number"] = str(
                found_incident.get("incident_number", "")
            )
            found_incident["title"] = str(found_incident.get("title", ""))
            found_incident["description"] = str(found_incident.get("description", ""))
            found_incident["status"] = str(found_incident.get("status", ""))
            found_incident["severity"] = str(found_incident.get("severity", ""))
            found_incident["incident_id"] = str(found_incident.get("incident_id", ""))
            found_incident["work_item_id"] = str(found_incident.get("work_item_id", ""))
            found_incident["created_at"] = str(found_incident.get("created_at", ""))
            found_incident["updated_at"] = str(found_incident.get("updated_at", ""))
            found_incident["resolved_at"] = str(found_incident.get("resolved_at", ""))
            found_incident["acknowledged_at"] = str(
                found_incident.get("acknowledged_at", "")
            )
            found_incident.pop("service_id", None)
            found_incident.pop("page_id", None)

            matching_incidents.append(found_incident)

        return json.dumps(
            {
                "success": True,
                "incidents": matching_incidents,
                "count": len(matching_incidents),
                "message": (
                    f"Retrieved {len(matching_incidents)} incident(s) "
                    f"from project '{project_id_str}'"
                ),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_incident",
                "description": "Retrieves incident(s) within a project. Supports two modes: "
                "(1) retrieving a specific incident by incident_number, or "
                "(2) retrieving all incidents in the project when incident_number is omitted. "
                "Use this to verify incident details before acknowledgment, check incident "
                "status and severity before blocking related work items, confirm incidents "
                "are resolved before resuming paused work, list all incidents related to tasks, "
                "and validate all incidents are closed before project closure.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The unique identifier of the project to query. ",
                        },
                        "incident_number": {
                            "type": "string",
                            "description": "The incident number to retrieve.",
                        },
                    },
                    "required": ["project_id"],
                },
            },
        }
