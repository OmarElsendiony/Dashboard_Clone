import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreatePage(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        document_id: str,
        title: str,
        content: Optional[str] = None
    ) -> str:
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(int(max(table.keys(), key=lambda x: int(x))) + 1)

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for pages"
            })
        
        pages = data.get("pages", {})
        documents = data.get("documents", {})
        
        if not document_id or not title:
            return json.dumps({
                "success": False,
                "error": "Missing parameters: document_id and title"
            })
        
        if str(document_id) not in documents:
            return json.dumps({
                "success": False,
                "error": f"Document with ID '{document_id}' not found"
            })
        
        new_page_id = generate_id(pages)
        
        new_page = {
            "page_id": str(new_page_id),
            "document_id": str(document_id),
            "title": str(title),
            "content": str(content) if content is not None else None,
            "type": None,
            "status": "draft",
            "created_at": "2026-02-11T23:59:00",
            "updated_at": "2026-02-11T23:59:00"
        }
        
        pages[str(new_page_id)] = new_page
        
        page_response = {
            "page_id": str(new_page_id),
            "document_id": str(document_id),
            "title": str(title),
            "content": str(content) if content is not None else None,
            "created_at": "2026-02-11T23:59:00",
            "updated_at": "2026-02-11T23:59:00"
        }
        
        return json.dumps({
            "success": True,
            "message": "Page created successfully",
            "page_id": str(new_page_id),
            "page_data": page_response
        })
        
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_page",
                "description": "Creates a new wiki page linked to a document.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "The ID of the parent document"
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the new page"
                        },
                        "content": {
                            "type": "string",
                            "description": "The main text content of the page. Optional — page will be created empty if not provided."
                        }
                    },
                    "required": ["document_id", "title"]
                }
            }
        }