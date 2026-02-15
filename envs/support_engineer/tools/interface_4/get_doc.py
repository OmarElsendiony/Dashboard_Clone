import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetDoc(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        document_id: Optional[str] = None,
        title: Optional[str] = None,
        related_ticket_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not any([document_id, title, related_ticket_id]):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one parameter must be provided",
                }
            )

        documents = data.get("documents", {})

        _EXCLUDE_KEYS = {
            "ingestion_channel",
            "kb_article_link",
            "incident_timestamp",
            "escalation_reason"
        }
        _EXCLUDE_PREFIXES = ("incident_", "escalation_", "space_")
        results = []
        for doc in documents.values():
            if document_id is not None and str(doc.get("document_id")) != str(
                document_id
            ):
                continue

            if title is not None and title.lower() not in doc.get("title", "").lower():
                continue

            if related_ticket_id is not None:
                doc_ticket_id = doc.get("related_ticket_id")
                if doc_ticket_id is None or str(doc_ticket_id) != str(
                    related_ticket_id
                ):
                    continue

            filtered_doc = {
                k: v
                for k, v in doc.items()
                if k not in _EXCLUDE_KEYS and not k.startswith(_EXCLUDE_PREFIXES)
            }
            results.append(filtered_doc)

        return json.dumps({"success": True, "documents": results, "count": len(results)})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_doc",
                "description": "Retrieve documentation for tickets, investigation records, or knowledge base articles.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "Filter by document identifier",
                        },
                        "title": {
                            "type": "string",
                            "description": "Filter by title substring",
                        },
                        "related_ticket_id": {
                            "type": "string",
                            "description": "Filter by related ticket identifier",
                        },
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["document_id"]},
                        {"required": ["title"]},
                        {"required": ["related_ticket_id"]},
                    ]
                },
            },
        }
