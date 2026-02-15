import json
from typing import Dict, Any
from tau_bench.envs.tool import Tool


class FetchDocumentationRecord(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        doc_name: str,
    ) -> str:
        documents = data.get("documents", {})

        if not doc_name:
            return json.dumps({"error": "doc_name is required"})

        document = None
        for doc in documents.values():
            if doc.get("doc_name") == str(doc_name):
                document = doc
                break

        if not document:
            return json.dumps(
                {"error": f"Document with name '{doc_name}' not found"}
            )

        return json.dumps({
            "success": True,
            "document": {
                "document_id": str(document["document_id"]),
                "title": str(document["title"]),
                "doc_name": str(document["doc_name"]),
                "description": str(document["description"]) if document.get("description") else None,
                "related_ticket_id": str(document["related_ticket_id"]) if document.get("related_ticket_id") else None,
                "status": str(document["status"]),
                "created_at": str(document["created_at"]),
                "updated_at": str(document["updated_at"]),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_documentation_record",
                "description": "Fetches the details of a document record. It should be used when you need to retrieve information about a specific documentation record.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "doc_name": {
                            "type": "string",
                            "description": "The name of the documentation record",
                        },
                    },
                    "required": ["doc_name"],
                },
            },
        }
