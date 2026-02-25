import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreateDoc(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        title: str,
        created_by: str,
        body: Optional[str] = None,
        program_id: Optional[str] = None
    ) -> str:
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(int(max(table.keys(), key=lambda x: int(x))) + 1)

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for documents"
            })
        
        documents = data.get("documents", {})
        projects = data.get("projects", {})
        users = data.get("users", {})
        
        if not title or not created_by:
            return json.dumps({
                "success": False,
                "error": "Missing parameters: title and created_by"
            })
            
        if str(created_by) not in users:
            return json.dumps({
                "success": False,
                "error": f"Creator with user_id '{created_by}' not found"
            })
        
        if program_id and str(program_id) not in projects:
            return json.dumps({
                "success": False,
                "error": f"Project with ID '{program_id}' not found"
            })
            
        new_doc_id = generate_id(documents)
        
        # Storing all fields in the DB object to match schema, forcing omitted fields to None
        new_doc = {
            "document_id": str(new_doc_id),
            "title": str(title),
            "body": str(body) if body is not None else None,
            "project_id": str(program_id) if program_id is not None else None,
            "status": "active",
            "created_by": str(created_by),
            "updated_by": None,
            "document_type": None,
            "incident_id": None,
            "created_at": "2026-02-11T23:59:00",
            "updated_at": "2026-02-11T23:59:00"
        }
        
        documents[str(new_doc_id)] = new_doc
        
        # Explicitly building response without incident_id or document_type
        doc_response = {
            "document_id": str(new_doc_id),
            "title": str(title),
            "body": str(body) if body is not None else None,
            "program_id": str(program_id) if program_id is not None else None,
            "status": "active",
            "created_by": str(created_by),
            "updated_by": None,
            "created_at": "2026-02-11T23:59:00",
            "updated_at": "2026-02-11T23:59:00"
        }
        
        return json.dumps({
            "success": True,
            "message": "Document created successfully",
            "document_id": str(new_doc_id),
            "document_data": doc_response
        })
        
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_doc",
                "description": "Creates a new document.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title of the new document"
                        },
                        "created_by": {
                            "type": "string",
                            "description": "User ID of the individual creating the document"
                        },
                        "body": {
                            "type": "string",
                            "description": "The main text body of the document"
                        },
                        "program_id": {
                            "type": "string",
                            "description": "The ID of the program the document belongs to"
                        }
                    },
                    "required": ["title", "created_by"]
                }
            }
        }