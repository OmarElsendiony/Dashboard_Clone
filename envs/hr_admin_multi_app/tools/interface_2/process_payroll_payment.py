import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool


class ProcessPayrollPayment(Tool):
    """
    Process payroll payments for a specific cycle with a given payment method.
    Creates payment records for all released payslips in the cycle.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        cycle_id: str,
        payment_method: str,
        status: Optional[str] = None,
        payment_date: Optional[str] = None,
    ) -> str:
        """
        Process payroll payments for all released payslips in a cycle.
        
        Args:
            data: Dictionary containing payments, payslips, employees, and payroll_cycles
            cycle_id: ID of the payroll cycle (required)
            payment_method: Payment method to use (required) - "Bank Transfer" or "Check"
            status: Optional payment status ('pending', 'completed', 'failed'). Defaults to 'pending'
            payment_date: Optional payment date in ISO format (YYYY-MM-DDTHH:MM:SS). If not provided, set to null
            
        Returns:
            JSON string with success status and list of created payments
        """
        
        # Validate data format
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format: 'data' must be a dict"}
            )
        
        payments = data.get("payments", {})
        if not isinstance(payments, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payments container: expected dict at data['payments']",
                }
            )
        
        payslips = data.get("payslips", {})
        if not isinstance(payslips, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payslips container: expected dict at data['payslips']",
                }
            )
        
        employees = data.get("employees", {})
        if not isinstance(employees, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid employees container: expected dict at data['employees']",
                }
            )
        
        payroll_cycles = data.get("payroll_cycles", {})
        if not isinstance(payroll_cycles, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payroll_cycles container: expected dict at data['payroll_cycles']",
                }
            )
        
        # Validate required fields
        if not cycle_id:
            return json.dumps(
                {"success": False, "error": "cycle_id is required"}
            )
        
        if not payment_method:
            return json.dumps(
                {"success": False, "error": "payment_method is required"}
            )
        
        cycle_id_str = str(cycle_id)
        
        # Validate status if provided
        if status is not None:
            valid_statuses = ["pending", "completed", "failed"]
            if status not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status value: '{status}'. Must be one of {valid_statuses}",
                    }
                )
        
        # Validate payment_date format if provided
        if payment_date is not None:
            # Basic validation for ISO datetime format (YYYY-MM-DDTHH:MM:SS)
            if not isinstance(payment_date, str) or len(payment_date) < 19:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Invalid payment_date format. Expected ISO datetime format: YYYY-MM-DDTHH:MM:SS",
                    }
                )
        
        # Validate cycle exists
        if cycle_id_str not in payroll_cycles:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Payroll cycle with ID '{cycle_id_str}' not found",
                }
            )
        
        # Validate payment_method
        valid_payment_methods = ["Bank Transfer", "Check"]
        if payment_method not in valid_payment_methods:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid payment_method value: '{payment_method}'. Must be one of {valid_payment_methods}",
                }
            )
        
        # Find all released payslips for this cycle
        released_payslips = []
        for payslip in payslips.values():
            if (
                payslip.get("cycle_id") == cycle_id_str
                and payslip.get("status") == "released"
            ):
                released_payslips.append(payslip)
        
        if not released_payslips:
            return json.dumps(
                {
                    "success": False,
                    "error": f"No released payslips found for cycle '{cycle_id_str}'. Only payslips with status 'released' can be processed for payment.",
                }
            )
        
        timestamp = "2025-12-12T12:00:00"
        
        # Generate payment ID
        def generate_payment_id(payments_dict: Dict[str, Any]) -> str:
            if not payments_dict:
                return "1"
            try:
                max_id = max(int(k) for k in payments_dict.keys() if k.isdigit())
                return str(max_id + 1)
            except ValueError:
                return "1"
        
        created_payments = []
        skipped_payslips = []
        
        # Create payments for each released payslip
        for payslip in released_payslips:
            payslip_id = payslip.get("payslip_id")
            employee_id = payslip.get("employee_id")
            
            # Check if payment already exists for this payslip
            payment_exists = False
            for existing_payment in payments.values():
                if existing_payment.get("source_payslip_id") == payslip_id:
                    payment_exists = True
                    skipped_payslips.append({
                        "payslip_id": payslip_id,
                        "employee_id": employee_id,
                        "reason": f"Payment already exists (payment_id: {existing_payment.get('payment_id')})",
                    })
                    break
            
            if payment_exists:
                continue
            
            # Create new payment
            new_payment_id = generate_payment_id(payments)
            
            # Set payment status (default to 'pending' if not provided)
            payment_status = status if status is not None else "pending"
            
            # Set payment_date (null if not provided, otherwise use provided value)
            final_payment_date = payment_date if payment_date is not None else None
            
            new_payment = {
                "payment_id": new_payment_id,
                "employee_id": employee_id,
                "source_payslip_id": payslip_id,
                "payment_method": payment_method,
                "amount": payslip.get("net_pay_value"),
                "status": payment_status,
                "payment_date": final_payment_date,
                "created_at": timestamp,
                "last_updated": timestamp,
            }
            
            payments[new_payment_id] = new_payment
            created_payments.append(new_payment)
        
        if not created_payments and not skipped_payslips:
            return json.dumps(
                {
                    "success": False,
                    "error": f"No payments were created for cycle '{cycle_id_str}'",
                }
            )
        
        message = f"Successfully processed payments for cycle '{cycle_id_str}'. Created {len(created_payments)} payment(s)"
        if skipped_payslips:
            message += f", skipped {len(skipped_payslips)} payslip(s) (payments already exist)"
        
        result = {
            "success": True,
            "message": message,
            "cycle_id": cycle_id_str,
            "payment_method": payment_method,
            "created_payments": created_payments,
            "created_count": len(created_payments),
            "skipped_payslips": skipped_payslips,
            "skipped_count": len(skipped_payslips),
        }
        
        # Include optional parameters in response if they were provided
        if status is not None:
            result["payment_status"] = status
        if payment_date is not None:
            result["payment_date"] = payment_date
        
        return json.dumps(result)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """
        Tool schema for function-calling.
        """
        return {
            "type": "function",
            "function": {
                "name": "process_payroll_payment",
                "description": (
                    "Process payroll payments for all released payslips in a specific cycle. "
                    "Creates payment records for each released payslip that doesn't already have a payment. "
                    "Requires cycle_id and payment_method. "
                    "Optionally accepts status ('pending', 'completed', 'failed') - defaults to 'pending'. "
                    "Optionally accepts payment_date in ISO format (YYYY-MM-DDTHH:MM:SS) - defaults to null. "
                    "Validates cycle exists and payment_method is valid ('Bank Transfer' or 'Check'). "
                    "Only processes payslips with status 'released'. "
                    "Skips payslips that already have associated payments. "
                    "Amount is automatically set from the payslip's net_pay_value. "
                    "Returns a list of created payments and any skipped payslips."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cycle_id": {
                            "type": "string",
                            "description": "ID of the payroll cycle (required)",
                        },
                        "payment_method": {
                            "type": "string",
                            "description": "Payment method to use (required). Valid values: 'Bank Transfer', 'Check'",
                            "enum": ["Bank Transfer", "Check"],
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional payment status. Valid values: 'pending', 'completed', 'failed'. Defaults to 'pending' if not provided.",
                            "enum": ["pending", "completed", "failed"],
                        },
                        "payment_date": {
                            "type": "string",
                            "description": "Optional payment date in ISO datetime format (YYYY-MM-DDTHH:MM:SS). If not provided, payment_date is set to null. Use this when marking a payment as 'completed'.",
                        },
                    },
                    "required": ["cycle_id", "payment_method"],
                },
            },
        }

