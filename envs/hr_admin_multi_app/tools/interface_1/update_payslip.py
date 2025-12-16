import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdatePayslip(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        payslip_id: str,
        status: Optional[str] = None,
        net_pay_value: Optional[float] = None,
    ) -> str:
        """
        Update payslip records in the payroll system.

        Args:
            data: Environment data containing payslips
            payslip_id: The payslip identifier (required)
            status: The payslip status - 'draft', 'released', 'updated' (optional)
            net_pay_value: Updated net pay amount (optional)
        """
        timestamp = "2025-11-16T23:59:00"
        payslips = data.get("payslips", {})

        # Validate required parameter
        if not payslip_id:
            return json.dumps(
                {"success": False, "error": "Missing required parameter: payslip_id"}
            )

        # Validate that payslip exists
        if payslip_id not in payslips:
            return json.dumps({"success": False, "error": f"Halt: Payslip not found"})

        # Validate at least one optional field is provided
        if status is None and net_pay_value is None:
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one optional parameter (status, net_pay_value) must be provided for updates",
                }
            )

        # Get current payslip
        current_payslip = payslips[payslip_id]

        # Validate status if provided
        if status is not None:
            valid_statuses = ["draft", "released", "updated"]
            if status not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Halt: Payslip operation failed - status must be one of: {', '.join(valid_statuses)}",
                    }
                )

        # Validate net_pay_value if provided
        if net_pay_value is not None:
            try:
                net_pay_value = float(net_pay_value)
                if net_pay_value <= 0:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "Halt: Payslip operation failed - net_pay_value must be positive",
                        }
                    )
            except (ValueError, TypeError):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Halt: Payslip operation failed - invalid net_pay_value format",
                    }
                )

        # Update payslip record
        updated_payslip = current_payslip.copy()

        if status is not None:
            updated_payslip["status"] = status

        if net_pay_value is not None:
            updated_payslip["net_pay_value"] = net_pay_value

        updated_payslip["last_updated"] = timestamp
        payslips[payslip_id] = updated_payslip

        return json.dumps(updated_payslip)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_payslip",
                "description": "Update payslip records in the payroll system. This tool modifies existing payslips while maintaining data integrity. Allows updates to payslip status and net pay amounts. Validates status values against accepted options ('draft', 'released', 'updated') and ensures net pay values remain positive. Essential for payroll corrections, payslip finalization, and maintaining accurate employee compensation records.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "payslip_id": {
                            "type": "string",
                            "description": "Payslip identifier (required, must exist in system)",
                        },
                        "status": {
                            "type": "string",
                            "description": "Payslip status: 'draft', 'released', 'updated' (optional)",
                        },
                        "net_pay_value": {
                            "type": "number",
                            "description": "Updated net pay amount (optional, must be positive monetary value)",
                        },
                    },
                    "required": ["payslip_id"],
                },
            },
        }
