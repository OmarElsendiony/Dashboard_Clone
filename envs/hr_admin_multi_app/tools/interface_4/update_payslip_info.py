import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpdatePayslipInfo(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        payslip_id: str,
        net_pay_value: Optional[float] = None,
        status: Optional[str] = None
    ) -> str:
        """
        Update an existing payslip record.
        Only provided fields will be updated.
        """
        payslips = data.get("payslips", {})
        timestamp = "2025-11-16T23:59:00"
        
        # Validate required parameter
        if not payslip_id:
            return json.dumps({
                "success": False,
                "error": "payslip_id is required"
            })
        
        # Validate payslip exists
        if payslip_id not in payslips:
            return json.dumps({
                "success": False,
                "error": f"payslip_id '{payslip_id}' does not reference a valid payslip"
            })
        
        payslip = payslips[payslip_id]
        
        # Check if at least one field is being updated
        if net_pay_value is None and status is None:
            return json.dumps({
                "success": False,
                "error": "At least one field must be provided to update"
            })
        
        # Validate status if provided
        if status is not None:
            valid_statuses = ["draft", "released", "updated"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                })
        
        # Update fields
        if net_pay_value is not None:
            payslip["net_pay_value"] = str(net_pay_value)
        if status is not None:
            payslip["status"] = status
        
        # Update timestamp
        payslip["last_updated"] = timestamp
        
        return json.dumps({
            "success": True,
            "payslip": payslip
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_payslip_info",
                "description": "Update an existing payslip record. Only provided fields will be updated.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "payslip_id": {
                            "type": "string",
                            "description": "Payslip ID (required)"
                        },
                        "net_pay_value": {
                            "type": "number",
                            "description": "Net pay value (optional)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Payslip status: draft, released, updated (optional)",
                            "enum": ["draft", "released", "updated"]
                        }
                    },
                    "required": ["payslip_id"]
                }
            }
        }
