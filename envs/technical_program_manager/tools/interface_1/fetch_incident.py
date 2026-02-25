import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class FetchIncident(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        incident_id: Optional[str] = None,
        incident_number: Optional[str] = None,
        program_id: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for incidents"
            })
        
        incidents = data.get("incidents", {})
        
        if not incident_id and not incident_number and not program_id and not severity and not status:
            return json.dumps({
                "success": False,
                "error": "At least one parameter (incident_id, incident_number, program_id, severity, or status) must be provided"
            })
            
        if severity:
            valid_severities = ["low", "medium", "high", "critical"]
            if severity not in valid_severities:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid severity '{severity}'. Must be one of: {', '.join(valid_severities)}"
                })
                
        if status:
            valid_statuses = ["open", "in_progress", "resolved", "closed"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
                })

        # Resolve incident_number to incident_id
        if incident_number and not incident_id:
            for iid, incident in incidents.items():
                if incident.get("incident_number") == str(incident_number):
                    incident_id = iid
                    break
            if not incident_id:
                return json.dumps({
                    "success": False,
                    "error": f"Incident with number '{incident_number}' not found"
                })
        
        if incident_id:
            if str(incident_id) not in incidents:
                return json.dumps({
                    "success": False,
                    "error": f"Incident with ID '{incident_id}' not found"
                })
            
            incident = incidents[str(incident_id)]
            
            if program_id and str(incident.get("project_id")) != str(program_id):
                return json.dumps({
                    "success": False,
                    "error": f"Incident does not belong to program '{program_id}'"
                })
            
            if severity and str(incident.get("severity")) != str(severity):
                return json.dumps({
                    "success": False,
                    "error": f"Incident severity is '{incident.get('severity')}', not '{severity}'"
                })
            
            if status and str(incident.get("status")) != str(status):
                return json.dumps({
                    "success": False,
                    "error": f"Incident status is '{incident.get('status')}', not '{status}'"
                })
            
            incident_data = {
                "incident_id": str(incident_id),
                "incident_number": str(incident.get("incident_number", "")) if incident.get("incident_number") is not None else None,
                "title": str(incident.get("title", "")) if incident.get("title") is not None else None,
                "description": str(incident.get("description", "")) if incident.get("description") is not None else None,
                "severity": str(incident.get("severity", "")) if incident.get("severity") is not None else None,
                "status": str(incident.get("status", "")) if incident.get("status") is not None else None,
                "program_id": str(incident.get("project_id", "")) if incident.get("project_id") is not None else None,
                "page_id": str(incident.get("page_id", "")) if incident.get("page_id") is not None else None,
                "work_item_id": str(incident.get("work_item_id", "")) if incident.get("work_item_id") is not None else None,
                "acknowledged_at": str(incident.get("acknowledged_at", "")) if incident.get("acknowledged_at") is not None else None,
                "resolved_at": str(incident.get("resolved_at", "")) if incident.get("resolved_at") is not None else None,
                "created_at": str(incident.get("created_at", "")) if incident.get("created_at") is not None else None,
                "updated_at": str(incident.get("updated_at", "")) if incident.get("updated_at") is not None else None
            }
            
            return json.dumps({
                "success": True,
                "incident_data": incident_data
            })
        
        if program_id or severity or status:
            found_incidents = []
            
            for iid, incident in incidents.items():
                if program_id and str(incident.get("project_id")) != str(program_id):
                    continue
                
                if severity and str(incident.get("severity")) != str(severity):
                    continue
                
                if status and str(incident.get("status")) != str(status):
                    continue
                
                incident_data = {
                    "incident_id": str(iid),
                    "incident_number": str(incident.get("incident_number", "")) if incident.get("incident_number") is not None else None,
                    "title": str(incident.get("title", "")) if incident.get("title") is not None else None,
                    "description": str(incident.get("description", "")) if incident.get("description") is not None else None,
                    "severity": str(incident.get("severity", "")) if incident.get("severity") is not None else None,
                    "status": str(incident.get("status", "")) if incident.get("status") is not None else None,
                    "program_id": str(incident.get("project_id", "")) if incident.get("project_id") is not None else None,
                    "page_id": str(incident.get("page_id", "")) if incident.get("page_id") is not None else None,
                    "work_item_id": str(incident.get("work_item_id", "")) if incident.get("work_item_id") is not None else None,
                    "acknowledged_at": str(incident.get("acknowledged_at", "")) if incident.get("acknowledged_at") is not None else None,
                    "resolved_at": str(incident.get("resolved_at", "")) if incident.get("resolved_at") is not None else None,
                    "created_at": str(incident.get("created_at", "")) if incident.get("created_at") is not None else None,
                    "updated_at": str(incident.get("updated_at", "")) if incident.get("updated_at") is not None else None
                }
                found_incidents.append(incident_data)
            
            if not found_incidents:
                return json.dumps({
                    "success": False,
                    "error": "No incidents found matching the specified filters"
                })
            
            if len(found_incidents) == 1:
                return json.dumps({
                    "success": True,
                    "incident_data": found_incidents[0]
                })
            
            return json.dumps({
                "success": True,
                "count": int(len(found_incidents)),
                "incidents": found_incidents
            })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_incident",
                "description": "Retrieves incident information. Use this to check incident status, get incident details for reporting, identify active incidents affecting projects, review incident severity and impact, or track incident resolution progress.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "incident_id": {
                            "type": "string",
                            "description": "The unique identifier of the incident"
                        },
                        "incident_number": {
                            "type": "string",
                            "description": "The human-readable incident number (e.g. INC-00012). Use this when the user references an incident by number."
                        },
                        "program_id": {
                            "type": "string",
                            "description": "Filter results by program ID"
                        },
                        "severity": {
                            "type": "string",
                            "description": "Filter results by severity. Valid values: low, medium, high, critical",
                            "enum": ["low", "medium", "high", "critical"]
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter results by status. Valid values: open, in_progress, resolved, closed",
                            "enum": ["open", "in_progress", "resolved", "closed"]
                        }
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["incident_id"]},
                        {"required": ["incident_number"]},
                        {"required": ["program_id"]},
                        {"required": ["severity"]},
                        {"required": ["status"]}
                    ]
                }
            }
        }