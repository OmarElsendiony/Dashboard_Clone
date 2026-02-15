import json
from typing import Dict, Any
from tau_bench.envs.tool import Tool


class ModifyDocumentationRecord(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        doc_name: str,
        new_status: str,
    ) -> str:
        documents = data.get("documents", {})
        timestamp = "2026-02-02 23:59:00"

        if not new_status:
            return json.dumps({"error": "new_status is required"})

        valid_statuses = ("WIP", "Verified", "Archived")
        if new_status not in valid_statuses:
            return json.dumps(
                {"error": f"Invalid status '{new_status}'. Must be one of: {', '.join(valid_statuses)}"}
            )

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

        document["status"] = new_status
        document["updated_at"] = timestamp

        return json.dumps({
            "success": True,
            "document": {
                "document_id": str(document["document_id"]),
                "doc_name": str(document["doc_name"]),
                "title": str(document["title"]),
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
                "name": "modify_documentation_record",
                "description": "Modifies the status of an existing documentation record. It should be used when there is a need to update the status of a documentation record.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "doc_name": {
                            "type": "string",
                            "description": "The name of the documentation record",
                        },
                        "new_status": {
                            "type": "string",
                            "description": "The new status for the documentation record",
                            "enum": ["WIP", "Verified", "Archived"],
                        },
                    },
                    "required": ["doc_name", "new_status"],
                },
            },
        }
