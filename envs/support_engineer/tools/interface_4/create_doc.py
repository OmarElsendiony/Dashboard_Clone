import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class CreateDoc(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        title: str,
        description: str,
        related_ticket_id: str,
    ) -> str:
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return json.dumps({
                    "success": bool(False),
                    "error": str("Wrong data format"),
                })
        if not isinstance(data, dict):
            return json.dumps({
                "success": bool(False),
                "error": str("Wrong data format"),
            })

        title_str = str(title).strip() if title is not None else ""
        if not title_str:
            return json.dumps({
                "success": bool(False),
                "error": str("title is required"),
            })

        description_str = str(description).strip() if description is not None else ""
        if not description_str:
            return json.dumps({
                "success": bool(False),
                "error": str("description is required"),
            })

        related_ticket_id_str = str(related_ticket_id).strip() if related_ticket_id is not None else ""
        if not related_ticket_id_str:
            return json.dumps({
                "success": bool(False),
                "error": str("related_ticket_id is required"),
            })

        tickets = data.get("tickets", {})
        documents = data.get("documents", {})

        if related_ticket_id_str not in tickets:
            return json.dumps({
                "success": bool(False),
                "error": str(f"Ticket with id '{related_ticket_id_str}' not found"),
            })

        if documents:
            max_id = max(int(k) for k in documents.keys())
            new_document_id = str(max_id + 1)
        else:
            new_document_id = str("1")

        static_timestamp = str("2026-02-02 23:59:00")

        new_document = {
            "document_id": str(new_document_id),
            "title": str(title_str),
            "description": str(description_str),
            "related_ticket_id": str(related_ticket_id_str),
            "created_at": str(static_timestamp),
            "updated_at": str(static_timestamp),
        }

        documents[new_document_id] = new_document

        exclude_keys = {
            "ingestion_channel",
            "kb_article_link",
            "incident_timestamp",
            "escalation_reason",
        }
        exclude_prefixes = ("incident_", "escalation_", "space_")
        document_response = {}
        for k, v in new_document.items():
            if k not in exclude_keys and not k.startswith(exclude_prefixes):
                document_response[k] = str(v)

        return json.dumps({
            "success": bool(True),
            "document": document_response,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_doc",
                "description": "Creates documentation for a ticket to capture knowledge and investigation records.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Document title summarizing the content",
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed documentation content",
                        },
                        "related_ticket_id": {
                            "type": "string",
                            "description": "Ticket identifier this document relates to",
                        },
                    },
                    "required": ["title", "description", "related_ticket_id"],
                },
            },
        }
