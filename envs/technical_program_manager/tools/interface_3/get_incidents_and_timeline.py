import json
import re
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class GetIncidentsAndTimeline(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        filter_field: Optional[str] = None,
        query: Optional[str] = None,
        sort: Optional[str] = None
    ) -> str:
        incidents = data.get("incidents", {})
        
        if query is not None and filter_field is None:
            return json.dumps({
                "success": bool(False),
                "error": str("Validation Error: A 'filter_field' must be selected when providing a 'query'.")
            })

        valid_fields = [
            "incident_id", "incident_number", "title", "description",
            "severity", "status", "service_id", "project_id", "page_id",
            "work_item_id", "acknowledged_at", "resolved_at",
            "created_at", "updated_at"
        ]

        if filter_field is not None and str(filter_field) not in valid_fields:
            return json.dumps({
                "success": bool(False),
                "error": str(f"Invalid filter_field '{filter_field}'. Allowed fields are: {', '.join(valid_fields)}")
            })

        valid_sorts = ["created_at", "updated_at"]
        if sort is not None and str(sort) not in valid_sorts:
            return json.dumps({
                "success": bool(False),
                "error": str(f"Invalid sort '{sort}'. Allowed sorts are: {', '.join(valid_sorts)}")
            })

        results = list()
        for inc_id, incident in incidents.items():
            if not isinstance(incident, dict):
                continue

            if filter_field is not None and query is not None:
                incident_val = incident.get(str(filter_field))
                if incident_val is None:
                    continue
                
                q_str = str(query)
                val_str = str(incident_val)

                if str(filter_field) in ["title", "description", "severity", "status"]:
                    q_lower = q_str.lower()
                    if q_lower not in val_str.lower():
                        try:
                            if not re.search(q_str, val_str, re.IGNORECASE):
                                continue
                        except re.error:
                            continue
                else:
                    if val_str != q_str:
                        continue
            
            incident_copy = dict(incident)
            incident_copy["incident_id"] = str(inc_id)
            results.append(dict(incident_copy))

        if sort is not None:
            results.sort(key=lambda x: str(x.get(str(sort), "")))

        return json.dumps({
            "success": bool(True),
            "incidents": list(results)
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_incidents_and_timeline",
                "description": (
                    "Purpose: Retrieves incident records and timeline data from the database. "
                    "When to Use: Use to fetch details of incidents, filter by specific attributes like severity or status, and extract timeline audit logs for root cause analysis or war room provisioning. "
                    "Returns: JSON object containing a success boolean and a list of matching incidents."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filter_field": {
                            "type": "string",
                            "description": (
                                "Optional. The column to filter by. Must be provided if 'query' is used. "
                                "Regex/partial match allowed for: title, description, severity (enum: low, medium, high, critical), status (enum: open, acknowledged, in_progress, resolved, closed). "
                                "Exact match strictly required for: incident_id, incident_number, service_id, project_id, page_id, work_item_id, acknowledged_at, resolved_at, created_at, updated_at."
                            ),
                            "enum": [
                                "incident_id", "incident_number", "title", "description",
                                "severity", "status", "service_id", "project_id", "page_id",
                                "work_item_id", "acknowledged_at", "resolved_at",
                                "created_at", "updated_at"
                            ]
                        },
                        "query": {
                            "type": "string",
                            "description": (
                                "Optional. The specific value to search for within the selected filter_field. "
                                "Supports regex and partial matching for 'title', 'description', 'severity', and 'status'. "
                                "Strictly enforces exact matches for 'incident_id', 'incident_number', 'service_id', 'project_id', 'page_id', 'work_item_id', 'acknowledged_at', 'resolved_at', 'created_at', and 'updated_at'."
                            )
                        },
                        "sort": {
                            "type": "string",
                            "description": "Optional. The timestamp field to sort the results by. Allowed values: created_at, updated_at.",
                            "enum": ["created_at", "updated_at"]
                        }
                    },
                    "required": []
                }
            }
        }
