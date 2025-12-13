import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetPayslipOrPayment(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        entity_type: str,
        payslip_id: Optional[str] = None,
        payment_id: Optional[str] = None,
        employee_id: Optional[str] = None,
        cycle_id: Optional[str] = None,
    ) -> str:
        """
        Fetches payslip or payment details based on the entity type and provided filters.
        """
        
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        # Validate required field
        if not entity_type:
            return json.dumps({
                "error": "Missing required parameter: entity_type"
            })

        # Validate entity_type
        valid_entity_types = ["payslip", "payment"]
        if entity_type not in valid_entity_types:
            return json.dumps({
                "error": f"Invalid entity_type. Must be one of: {', '.join(valid_entity_types)}"
            })

        if entity_type == "payslip":
            payslips = data.get("payslips", {})
            
            # If specific payslip_id is provided
            if payslip_id:
                if payslip_id not in payslips:
                    return json.dumps({
                        "error": f"Payslip with ID '{payslip_id}' not found"
                    })
                
                return json.dumps({
                    "success": True,
                    "entity_type": "payslip",
                    "payslip_data": payslips[payslip_id]
                })
            
            # Filter payslips based on provided criteria
            results = []
            for payslip in payslips.values():
                match = True
                if employee_id and payslip.get("employee_id") != employee_id:
                    match = False
                if cycle_id and payslip.get("cycle_id") != cycle_id:
                    match = False
                if match:
                    results.append(payslip)
            
            return json.dumps({
                "success": True,
                "entity_type": "payslip",
                "count": len(results),
                "results": results
            })
        
        elif entity_type == "payment":
            payments = data.get("payments", {})
            
            # If specific payment_id is provided
            if payment_id:
                if payment_id not in payments:
                    return json.dumps({
                        "error": f"Payment with ID '{payment_id}' not found"
                    })
                
                return json.dumps({
                    "success": True,
                    "entity_type": "payment",
                    "payment_data": payments[payment_id]
                })
            
            # Filter payments based on provided criteria
            results = []
            for payment in payments.values():
                match = True
                if employee_id and payment.get("employee_id") != employee_id:
                    match = False
                if cycle_id and payment.get("cycle_id") != cycle_id:
                    match = False
                if match:
                    results.append(payment)
            
            return json.dumps({
                "success": True,
                "entity_type": "payment",
                "count": len(results),
                "results": results
            })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_payslip_or_payment",
                "description": "Fetches payslip or payment details from the HR payroll system.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entity_type": {
                            "type": "string",
                            "description": "Type of entity to fetch: 'payslip' or 'payment' (required)"
                        },
                        "payslip_id": {
                            "type": "string",
                            "description": "ID of the specific payslip to retrieve (optional, used with entity_type='payslip')"
                        },
                        "payment_id": {
                            "type": "string",
                            "description": "ID of the specific payment to retrieve (optional, used with entity_type='payment')"
                        },
                        "employee_id": {
                            "type": "string",
                            "description": "Filter by employee ID (optional)"
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "Filter by payroll cycle ID (optional)"
                        }
                    },
                    "required": ["entity_type"]
                }
            }
        }
