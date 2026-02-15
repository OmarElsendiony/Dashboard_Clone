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
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not title:
            return json.dumps({"success": False, "error": "title is required"})

        if not description:
            return json.dumps(
                {"success": False, "error": "description is required"}
            )

        if not related_ticket_id:
            return json.dumps(
                {"success": False, "error": "related_ticket_id is required"}
            )

        tickets = data.get("tickets", {})
        documents = data.get("documents", {})

        if str(related_ticket_id) not in tickets:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Ticket with id '{related_ticket_id}' not found",
                }
            )

        if documents:
            max_id = max(int(k) for k in documents.keys())
            new_document_id = str(max_id + 1)
        else:
            new_document_id = "1"

        static_timestamp = "2026-02-02 23:59:00"

        new_document = {
            "document_id": new_document_id,
            "title": title,
            "description": description,
            "related_ticket_id": related_ticket_id,
            "created_at": static_timestamp,
            "updated_at": static_timestamp,
        }

        documents[new_document_id] = new_document

        _EXCLUDE_KEYS = {
            "ingestion_channel",
            "kb_article_link",
            "incident_timestamp",
            "escalation_reason"
        }
        _EXCLUDE_PREFIXES = ("incident_", "escalation_", "space_")
        document_response = {
            k: v
            for k, v in new_document.items()
            if k not in _EXCLUDE_KEYS and not k.startswith(_EXCLUDE_PREFIXES)
        }
        return json.dumps({"success": True, "document": document_response})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_doc",
                "description": "Create documentation for a ticket to capture knowledge and investigation records.",
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
