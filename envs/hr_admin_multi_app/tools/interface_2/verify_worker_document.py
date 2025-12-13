import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class VerifyWorkerDocument(Tool):
    """
    Verify/update the status of a worker document.
    Used to mark documents as accepted or rejected during HR processes like exit clearance.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        document_id: Optional[str] = None,
        status: Optional[str] = None,
        employee_id: Optional[str] = None,
    ) -> str:
        """
        Update the verification status of a worker document.
        
        Args:
            data: Dictionary containing documents
            document_id: ID of the document to verify (optional)
            status: New verification status - must be 'accepted' or 'rejected' (optional)
            employee_id: ID of the employee (optional) - can filter documents by employee
            
        Returns:
            JSON string with success status and updated document details
        """
        
        timestamp = "2025-12-12T12:00:00"
        
        # Validate data format
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format: 'data' must be a dict"}
            )
        
        documents = data.get("documents", {})
        if not isinstance(documents, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid documents container: expected dict at data['documents']",
                }
            )
        
        # Validate at least one identifier is provided
        if not document_id and not employee_id:
            return json.dumps(
                {"success": False, "error": "At least one of document_id or employee_id is required"}
            )
        
        # Find document by provided identifier(s)
        document = None
        document_id_str = None
        
        # Priority 1: By document_id
        if document_id:
            document_id_str = str(document_id)
            if document_id_str in documents:
                document = documents[document_id_str]
                
                # If employee_id also provided, validate it matches
                if employee_id:
                    employee_id_str = str(employee_id)
                    if document.get("employee_id") != employee_id_str:
                        return json.dumps(
                            {
                                "success": False,
                                "error": f"Document ID '{document_id_str}' belongs to employee '{document.get('employee_id')}', not '{employee_id_str}'",
                            }
                        )
        
        # Priority 2: By employee_id only
        if not document and employee_id:
            employee_id_str = str(employee_id)
            # Find first document for this employee
            for doc_id, doc in documents.items():
                if doc.get("employee_id") == employee_id_str:
                    document = doc
                    document_id_str = doc_id
                    break
        
        # If document not found with any identifier
        if not document:
            identifiers = []
            if document_id:
                identifiers.append(f"document_id='{document_id}'")
            if employee_id:
                identifiers.append(f"employee_id='{employee_id}'")
            return json.dumps(
                {
                    "success": False,
                    "error": f"Document not found with provided identifiers: {', '.join(identifiers)}",
                }
            )
        
        # If status provided, validate and update
        if status:
            valid_statuses = ["accepted", "rejected"]
            if status not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}",
                    }
                )
            
            old_status = document.get("status")
            
            # Update document status
            document["status"] = status
            document["last_updated"] = timestamp
            
            return json.dumps(
                {
                    "success": True,
                    "message": f"Document '{document.get('title')}' (ID: {document_id_str}) status updated from '{old_status}' to '{status}'",
                    "document": document,
                }
            )
        else:
            # No status provided, just return the document
            return json.dumps(
                {
                    "success": True,
                    "message": f"Document '{document.get('title')}' (ID: {document_id_str}) retrieved successfully. No status update performed.",
                    "document": document,
                }
            )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """
        Tool schema for function-calling.
        """
        return {
            "type": "function",
            "function": {
                "name": "verify_worker_document",
                "description": (
                    "Verify and update the status of a worker document. "
                    "Can identify documents by document_id or employee_id (at least one required). "
                    "Used during HR processes like exit clearance to mark documents as accepted or rejected. "
                    "For example, during exit clearance processing, you would verify and update document status. "
                    "Status parameter is optional - if not provided, the tool retrieves the document without updating. "
                    "Valid statuses: 'accepted', 'rejected'. "
                    "Document types include: employee, onboarding, offboarding, payroll_input, payroll_earning, "
                    "payroll_deduction, payslip."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "ID of the document to verify (optional, but at least one identifier required)",
                        },
                        "status": {
                            "type": "string",
                            "description": "New verification status (optional). Must be 'accepted' or 'rejected'. If not provided, the document is retrieved without status update.",
                            "enum": ["accepted", "rejected"],
                        },
                        "employee_id": {
                            "type": "string",
                            "description": "ID of the employee (optional, but at least one identifier required). Can be used to find documents belonging to a specific employee.",
                        },
                    },
                    "required": [],
                },
            },
        }

