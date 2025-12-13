import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class GetAssets(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], employee_id: Optional[str] = None, status: Optional[str] = None, email: Optional[str] = None) -> str:
        """
        Retrieve employee asset records with optional filtering.
        
        Args:
            data: Environment data containing employee_assets and employees
            employee_id: Filter by employee identifier (optional)
            status: Filter by asset status - 'returned', 'missing', 'damaged', 'assigned' (optional)
            email: Filter by employee email address (optional)
        """
        employees = data.get("employees", {})
        employee_assets = data.get("employee_assets", {})
        
        # Validate employee_id if provided
        if employee_id is not None and employee_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"Halt: Employee not found"
            })
        
        # Validate email if provided and find matching employee_id
        email_matched_employee_id = None
        if email is not None:
            found = False
            for emp_id, emp_data in employees.items():
                if emp_data.get("email") == email:
                    email_matched_employee_id = emp_id
                    found = True
                    break
            if not found:
                return json.dumps({
                    "success": False,
                    "error": f"Halt: Employee with email not found"
                })
        
        # Validate status if provided
        if status is not None:
            valid_statuses = ["returned", "missing", "damaged", "assigned"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Halt: Invalid asset status - status must be one of: {', '.join(valid_statuses)}"
                })
        
        # Determine which employee_id to use for filtering
        filter_employee_id = employee_id if employee_id is not None else email_matched_employee_id
        
        # Filter assets based on criteria
        filtered_assets = []
        
        for asset_id, asset in employee_assets.items():
            # Apply employee_id filter (from either employee_id or email)
            if filter_employee_id is not None and asset.get("employee_id") != filter_employee_id:
                continue
            
            # Apply status filter
            if status is not None and asset.get("status") != status:
                continue
            
            # Add asset_id to the result
            asset_with_id = asset.copy()
            asset_with_id["asset_id"] = asset_id
            
            # Enrich with employee information if available
            emp_id = asset.get("employee_id")
            if emp_id in employees:
                employee = employees[emp_id]
                asset_with_id["employee_name"] = employee.get("full_name")
                asset_with_id["employee_email"] = employee.get("email")
            
            filtered_assets.append(asset_with_id)
        
        # Calculate summary statistics
        summary = {
            "total_assets": len(filtered_assets),
            "by_status": {}
        }
        
        # Count assets by status
        for asset in filtered_assets:
            asset_status = asset.get("status", "unknown")
            summary["by_status"][asset_status] = summary["by_status"].get(asset_status, 0) + 1
        
        # If filtering by employee, add employee-specific summary
        if filter_employee_id is not None:
            employee = employees.get(filter_employee_id, {})
            summary["employee_info"] = {
                "employee_id": filter_employee_id,
                "employee_name": employee.get("full_name"),
                "employee_email": employee.get("email"),
                "employee_status": employee.get("status")
            }
        
        return json.dumps({
            "success": True,
            "summary": summary,
            "assets": filtered_assets
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_assets",
                "description": "Retrieve employee asset records with optional filtering capabilities. This tool allows querying of company assets assigned to employees with flexible filtering by employee identifier, email address, and asset status. Returns comprehensive asset information including asset details, employee information, and summary statistics. Supports filtering by status: 'returned', 'missing', 'damaged'. Enriches results with employee names and emails for better context. Essential for asset tracking, offboarding verification, settlement calculations, and inventory management.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "Employee identifier to filter assets (optional, must exist in system if provided)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Asset status to filter by: 'returned', 'missing', 'damaged', 'assigned' (optional)",
                        },
                        "email": {
                            "type": "string",
                            "description": "Employee email address to filter assets (optional, must exist in system if provided)"
                        }
                    },
                    "required": []
                }
            }
        }