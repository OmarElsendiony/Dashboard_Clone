import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpdatePage(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        page_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for pages"
            })
        
        pages = data.get("pages", {})
        
        if not page_id:
            return json.dumps({
                "success": False,
                "error": "Missing parameter: page_id"
            })
            
        if str(page_id) not in pages:
            return json.dumps({
                "success": False,
                "error": f"Page with ID '{page_id}' not found"
            })
            
        if title is None and content is None:
            return json.dumps({
                "success": False,
                "error": "At least one field to update must be provided"
            })
            
        page = pages[str(page_id)]
        updated_page = page.copy()
        
        if title is not None:
            updated_page["title"] = str(title)
        if content is not None:
            updated_page["content"] = str(content)
            
        updated_page["updated_at"] = "2026-02-11T23:59:00"
        
        pages[str(page_id)] = updated_page
        
        page_response = {
            "page_id": str(page_id),
            "document_id": str(updated_page.get("document_id", "")) if updated_page.get("document_id") is not None else None,
            "title": str(updated_page.get("title", "")) if updated_page.get("title") is not None else None,
            "content": str(updated_page.get("content", "")) if updated_page.get("content") is not None else None,
            "created_at": str(updated_page.get("created_at", "")) if updated_page.get("created_at") is not None else None,
            "updated_at": str(updated_page.get("updated_at", "")) if updated_page.get("updated_at") is not None else None
        }
        
        return json.dumps({
            "success": True,
            "message": f"Page '{page_id}' updated successfully",
            "page_data": page_response
        })
        
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_page",
                "description": "Edits the title or content of an existing wiki page.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "page_id": {
                            "type": "string",
                            "description": "The unique identifier of the page to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "The new title of the page"
                        },
                        "content": {
                            "type": "string",
                            "description": "The new content text of the page"
                        }
                    },
                    "required": ["page_id"]
                }
            }
        }