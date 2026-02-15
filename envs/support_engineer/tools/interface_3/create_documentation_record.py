import json
from typing import Dict, Optional, Any
from tau_bench.envs.tool import Tool


class CreateDocumentationRecord(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        doc_name: str,
        title: str,
        ticket_number: str,
        description: Optional[str] = None,
    ) -> str:
        documents = data.get("documents", {})
        tickets = data.get("tickets", {})
        timestamp = "2026-02-02 23:59:00"

        if not doc_name:
            return json.dumps({"error": "doc_name is required"})

        for doc in documents.values():
            if doc.get("doc_name") == str(doc_name):
                return json.dumps(
                    {"error": f"A document with name '{doc_name}' already exists"}
                )

        if not title:
            return json.dumps({"error": "title is required"})

        if not ticket_number:
            return json.dumps({"error": "ticket_number is required"})

        ticket_id = None
        for t_id, ticket in tickets.items():
            if ticket.get("ticket_number") == str(ticket_number):
                ticket_id = t_id
                break

        if not ticket_id:
            return json.dumps({"error": f"Ticket with number '{ticket_number}' not found"})

        if not documents:
            new_id = "1"
        else:
            new_id = str(max(int(k) for k in documents.keys()) + 1)

        new_document = {
            "document_id": new_id,
            "doc_name": str(doc_name),
            "title": str(title),
            "description": str(description) if description else None,
            "related_ticket_id": str(ticket_id),
            "linked_pull_request_id": None,
            "status": "WIP",
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        documents[new_id] = new_document

        return json.dumps({
            "success": True,
            "document": {
                "document_id": str(new_document["document_id"]),
                "doc_name": str(new_document["doc_name"]),
                "title": str(new_document["title"]),
                "description": new_document["description"],
                "related_ticket_id": str(new_document["related_ticket_id"]),
                "status": str(new_document["status"]),
                "created_at": str(new_document["created_at"]),
                "updated_at": str(new_document["updated_at"]),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_documentation_record",
                "description": "Creates a new document record to track a ticket throughout its lifecycle.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "doc_name": {
                            "type": "string",
                            "description": "The name of the documentation record",
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the documentation record",
                        },
                        "ticket_number": {
                            "type": "string",
                            "description": "The ticket number to associate with this documentation record",
                        },
                        "description": {
                            "type": "string",
                            "description": "The description or details for the documentation record",
                        },
                    },
                    "required": ["doc_name", "title", "ticket_number"],
                },
            },
        }
