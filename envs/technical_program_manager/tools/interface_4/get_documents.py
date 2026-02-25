import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class GetDocuments(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        document_id: Optional[str] = None,
        title: Optional[str] = None,
        project_id: Optional[str] = None,
        incident_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not any([document_id, title, project_id, incident_id]):
            return json.dumps({
                "success": False,
                "error": "At least one filter parameter must be provided",
            })

        document_id_str = str(document_id).strip() if document_id else None
        title_str = str(title).strip() if title else None
        project_id_str = str(project_id).strip() if project_id else None
        incident_id_str = str(incident_id).strip() if incident_id else None

        documents = data.get("documents", {})
        projects = data.get("projects", {})
        incidents = data.get("incidents", {})

        if project_id_str is not None and project_id_str not in projects:
            return json.dumps({"success": False, "error": f"Project '{project_id_str}' not found"})

        if incident_id_str is not None and incident_id_str not in incidents:
            return json.dumps({"success": False, "error": f"Incident '{incident_id_str}' not found"})

        results = []
        for doc in documents.values():
            if document_id_str is not None and str(doc.get("document_id", "")) != document_id_str:
                continue

            if title_str is not None and title_str.lower() != str(doc.get("title", "")).lower():
                continue

            if project_id_str is not None and str(doc.get("project_id", "")) != project_id_str:
                continue

            if incident_id_str is not None:
                doc_incident = doc.get("incident_id")
                if doc_incident is None or str(doc_incident) != incident_id_str:
                    continue

            filtered_doc = {
                "document_id": str(doc.get("document_id", "")),
                "title": str(doc.get("title", "")),
                "body": str(doc.get("body", "")) if doc.get("body") else None,
                "project_id": str(doc.get("project_id", "")) if doc.get("project_id") else None,
                "incident_id": str(doc.get("incident_id", "")) if doc.get("incident_id") else None,
                "created_at": str(doc.get("created_at", "")),
                "updated_at": str(doc.get("updated_at", "")),
            }
            results.append(filtered_doc)
        results.sort(key=lambda x: int(x["document_id"]))
        return json.dumps({"success": True, "documents": results, "count": int(len(results))})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_documents",
                "description": "Retrieves document records based on optional filter criteria.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "Filter by the exact unique document identifier (document_id).",
                        },
                        "title": {
                            "type": "string",
                            "description": "Filter by document title (exact, case-insensitive).",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Filter by the project identifier (project_id).",
                        },
                        "incident_id": {
                            "type": "string",
                            "description": "Filter by the linked incident identifier (incident_id).",
                        },
                    },
                    "anyOf": [
                        {"required": ["document_id"]},
                        {"required": ["title"]},
                        {"required": ["project_id"]},
                        {"required": ["incident_id"]},
                    ],
                    "required": [],
                },
            },
        }
