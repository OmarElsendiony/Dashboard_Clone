import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetWorkDocument(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        project_id: Optional[str] = None,
        incident_id: Optional[str] = None,
        status: Optional[str] = None,
        title_contains: Optional[str] = None,
    ) -> str:
        # 1. Basic data integrity check
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        # 2. Validate that at least one filter is provided
        if not any([project_id, incident_id, status, title_contains]):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one filter must be provided (project_id, incident_id, status, or title_contains)",
                }
            )

        # 3. Validate status enum if provided
        valid_statuses = ["active", "published", "approved"]
        if status and status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}",
                }
            )

        documents = data.get("documents", {})
        pages = data.get("pages", {})

        # 4. Filtering Logic
        results = []

        for doc_id, doc in documents.items():
            # Apply filters
            if project_id and str(doc.get("project_id")) != project_id:
                continue
            if incident_id and str(doc.get("incident_id")) != incident_id:
                continue
            if status and str(doc.get("status")) != status:
                continue
            if (
                title_contains
                and str(title_contains.lower()) not in doc.get("title", "").lower()
            ):
                continue

            # Enrich document with its associated pages/content if available
            doc_copy = doc.copy()
            doc_pages = [p for p in pages.values() if p["document_id"] == doc_id]
            doc_copy["pages"] = doc_pages

            results.append(doc_copy)

        if not results:
            # Type cast empty response
            response = {
                "success": bool(False),
                "message": str("No documents found matching the specified filters."),
                "documents": list([]),
            }
            return json.dumps(response)

        # Type cast all values in each document and page
        typed_documents = []
        for doc in results:
            typed_doc = {}
            for key, value in doc.items():
                if key == "pages":
                    # Type cast pages separately
                    typed_pages = []
                    for page in value:
                        typed_page = {}
                        for page_key, page_value in page.items():
                            if page_value is None:
                                typed_page[page_key] = None
                            elif page_key in [
                                "document_id",
                                "page_id",
                                "content",
                                "created_at",
                                "updated_at",
                            ]:
                                typed_page[page_key] = (
                                    str(page_value) if page_value is not None else None
                                )
                            elif isinstance(page_value, bool):
                                typed_page[page_key] = bool(page_value)
                            elif isinstance(page_value, int):
                                typed_page[page_key] = int(page_value)
                            elif isinstance(page_value, float):
                                typed_page[page_key] = float(page_value)
                            elif isinstance(page_value, list):
                                typed_page[page_key] = list(page_value)
                            elif isinstance(page_value, dict):
                                typed_page[page_key] = dict(page_value)
                            else:
                                typed_page[page_key] = page_value
                        typed_pages.append(typed_page)
                    typed_doc[key] = list(typed_pages)
                elif value is None:
                    typed_doc[key] = None
                elif key in [
                    "document_id",
                    "project_id",
                    "incident_id",
                    "title",
                    "status",
                    "document_type",
                    "created_at",
                    "updated_at",
                    "published_at",
                ]:
                    typed_doc[key] = str(value) if value is not None else None
                elif isinstance(value, bool):
                    typed_doc[key] = bool(value)
                elif isinstance(value, int):
                    typed_doc[key] = int(value)
                elif isinstance(value, float):
                    typed_doc[key] = float(value)
                elif isinstance(value, list):
                    typed_doc[key] = list(value)
                elif isinstance(value, dict):
                    typed_doc[key] = dict(value)
                else:
                    typed_doc[key] = value
            typed_documents.append(typed_doc)

        # Type cast all values and build response object
        response = {
            "success": bool(True),
            "message": str(
                f"Successfully retrieved {len(typed_documents)} document(s)."
            ),
            "documents": list(typed_documents),
        }

        return json.dumps(response)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_work_document",
                "description": "Searches for and retrieves technical documentation, architectural pivots, or incident learning records from the system registry. Use to find 'Pivot Logs' that authorize scope changes, or to verify if an RCA exists 48 hours after an incident is resolved.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Filter by associated Project UUID.",
                        },
                        "incident_id": {
                            "type": "string",
                            "description": "Filter by associated Incident UUID.",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["active", "published", "approved"],
                            "description": "Filter by the document's current lifecycle state.",
                        },
                        "title_contains": {
                            "type": "string",
                            "description": "Case-insensitive keyword search for the document title (e.g., 'Pivot' or 'RCA').",
                        },
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["project_id"]},
                        {"required": ["incident_id"]},
                        {"required": ["status"]},
                        {"required": ["title_contains"]},
                    ],
                },
            },
        }
