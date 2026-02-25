import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class UpdateDocument(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        document_id: str,
        status: str,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'data' must be a dict"
            })

        document_id_clean = str(document_id).strip() if document_id is not None else ""
        status_clean = str(status).strip() if status is not None else ""

        if not document_id_clean:
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: 'document_id'"
            })

        if not status_clean:
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: 'status'"
            })

        documents_dict = data.get("documents", {})

        if not isinstance(documents_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'documents' must be a dict"
            })

        if document_id_clean not in documents_dict:
            return json.dumps({
                "success": False,
                "error": f"Document with id '{document_id_clean}' not found"
            })
        
        if status_clean != "published":
            return json.dumps({
                "success": False,
                "error": "Invalid status. The status should be 'published'"
            })

        document_record = documents_dict[document_id_clean]
        current_status = str(document_record.get("status", "")).strip()

        if current_status == "published":
            return json.dumps({
                "success": False,
                "error": "published documents cannot be re-published"
            })

        document_record["status"] = status_clean
        timestamp = "2026-02-11T23:59:00"
        document_record["updated_at"] = timestamp
        document_record["published_at"] = timestamp

        documents_dict[document_id_clean] = document_record

        response_document = {
            "document_id": str(document_id_clean),
            "document_title": str(document_record.get("title", "")),
            "project_id": str(document_record.get("project_id", "")),
            "status": str(document_record.get("status", "")),
            "created_by": str(document_record.get("created_by", "")),
            "created_at": str(document_record.get("created_at", "")),
            "updated_at": str(document_record.get("updated_at", "")),
            "published_at": str(document_record.get("published_at", "")),
        }

        return json.dumps({
            "success": True,
            "document": response_document,
            "message": "document published successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_document",
                "description":  "Updates the status of a project document. "
                                "Ensures the document was not published already and approves the documents which are 'active' or approved,"
                                "can be used during the project closure to approve the files.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "The unique identifier of the project document."
                        },
                        "status": {
                            "type": "string",
                            "enum": ["published"],
                            "description": "The lifecycle status of the document."
                        }
                    },
                    "required": ["document_id", "status"]
                }
            }
        }