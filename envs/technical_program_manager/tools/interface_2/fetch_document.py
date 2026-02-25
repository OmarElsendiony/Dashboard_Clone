import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class FetchDocument(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        project_id: str,
        title: str,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'data' must be a dict"
            })

        if not project_id:
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: 'project_id'"
            })

        if not title:
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: 'title'"
            })

        documents_dict = data.get("documents", {})

        if not isinstance(documents_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'documents' must be a dict"
            })

        project_id_clean = str(project_id).strip()
        title_clean = str(title).strip()

        matched_document = None
        matched_document_id = None

        for doc_id, doc_data in documents_dict.items():

            if str(doc_data.get("project_id", "")).strip() != project_id_clean:
                continue

            if str(doc_data.get("title", "")).strip() == title_clean:
                matched_document = doc_data
                matched_document_id = doc_id
                break

        if not matched_document:
            return json.dumps({
                "success": False,
                "error": "Document not found for the given project and title"
            })

        response_document = {
            "document_id": str(matched_document_id),
            "title": str(matched_document.get("title", "")),
            "body": str(matched_document.get("body", "")),
            "project_id": str(matched_document.get("project_id", "")),
            "status": str(matched_document.get("status", "")),
            "created_by": str(matched_document.get("created_by", "")),
            "updated_by": str(matched_document.get("updated_by", "")),
            "incident_id": str(matched_document.get("incident_id", "")),
            "created_at": str(matched_document.get("created_at", "")),
            "updated_at": str(matched_document.get("updated_at", ""))
        }

        return json.dumps({
            "success": True,
            "document": response_document
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_document",
                "description": "Retrieves document details within a specific project context using project_id and title. "
                               "This function validates that the document exists before reviewing requirements, "
                               "Use this before post-incident analysis, or other project documentation in TPM workflows.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The unique identifier of the project containing the document."
                        },
                        "title": {
                            "type": "string",
                            "description": "The exact title of the document to retrieve."
                        }
                    },
                    "required": ["project_id", "title"]
                }
            }
        }
