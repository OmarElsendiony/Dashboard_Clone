import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UploadDocument(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        document_url: str,
        document_type: str,
        title: Optional[str] = None,
        target_entity: Optional[str] = None,
        entity_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        """
        Upload a document for an employee. The document_url can be text content.
        """
        documents = data.get("documents", {})
        employees = data.get("employees", {})
        timestamp = "2025-11-16T23:59:00"
        
        # Validate required fields
        if not employee_id:
            return json.dumps({
                "success": False,
                "error": "employee_id is required"
            })
        
        if not document_url:
            return json.dumps({
                "success": False,
                "error": "document_url is required"
            })
        
        if not document_type:
            return json.dumps({
                "success": False,
                "error": "document_type is required"
            })
        
        # Validate employee exists
        if employee_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"employee_id '{employee_id}' does not reference a valid employee"
            })
        
        # Validate document_type
        valid_document_types = ["onboarding", "offboarding", "employee", "payroll_input", "payroll_earning", "payroll_deduction", "payslip"]
        if document_type not in valid_document_types:
            return json.dumps({
                "success": False,
                "error": f"Invalid document_type. Must be one of: {', '.join(valid_document_types)}"
            })
        
        # Validate status if provided
        if status:
            valid_statuses = ["accepted", "rejected"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                })
        
        # Generate new document_id
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        new_document_id = generate_id(documents)
        
        # Set default target_entity to employee_id if not provided
        if target_entity is None:
            target_entity = employee_id
        
        # Set default entity_type to "employee" if not provided
        if entity_type is None:
            entity_type = "employee"
        
        # Create new document record
        new_document = {
            "document_id": new_document_id,
            "employee_id": employee_id,
            "document_url": document_url,  # This can be text content
            "title": title,
            "document_type": document_type,
            "target_entity": target_entity,
            "entity_type": entity_type,
            "status": status
        }
        
        documents[new_document_id] = new_document
        
        return json.dumps({
            "success": True,
            "document": new_document
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "upload_document",
                "description": "Upload a document for an employee. The document_url can be text content. Validates employee exists and document_type is valid.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "Employee ID (required)"
                        },
                        "document_url": {
                            "type": "string",
                            "description": "Document URL or text content (required)"
                        },
                        "document_type": {
                            "type": "string",
                            "description": "Type of document: onboarding, offboarding, employee, payroll_input, payroll_earning, payroll_deduction, payslip (required)",
                            "enum": ["onboarding", "offboarding", "employee", "payroll_input", "payroll_earning", "payroll_deduction", "payslip"]
                        },
                        "title": {
                            "type": "string",
                            "description": "Document title (optional)"
                        },
                        "target_entity": {
                            "type": "string",
                            "description": "Target entity ID (optional, defaults to employee_id)"
                        },
                        "entity_type": {
                            "type": "string",
                            "description": "Entity type (optional, defaults to 'employee')"
                        },
                        "status": {
                            "type": "string",
                            "description": "Document status: accepted, rejected (optional)",
                            "enum": ["accepted", "rejected"]
                        }
                    },
                    "required": ["employee_id", "document_url", "document_type"]
                }
            }
        }
