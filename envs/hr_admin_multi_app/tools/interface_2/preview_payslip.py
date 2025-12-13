import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class PreviewPayslip(Tool):
    """
    Preview (retrieve) payslips with flexible filtering options.
    Can retrieve by specific payslip ID or filter by employee, cycle, or status.
    Used to verify payslip exists and check its status before operations like release.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        payslip_id: Optional[str] = None,
        employee_id: Optional[str] = None,
        cycle_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        """
        Preview payslip(s) with optional filtering.
        
        Args:
            data: Dictionary containing payslips
            payslip_id: Optional ID of a specific payslip to retrieve
            employee_id: Optional employee ID to filter payslips
            cycle_id: Optional cycle ID to filter payslips
            status: Optional status to filter payslips ('draft', 'updated', 'released')
            
        Returns:
            JSON string with success status and payslip details
        """
        
        # Validate data format
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format: 'data' must be a dict"}
            )
        
        payslips = data.get("payslips", {})
        if not isinstance(payslips, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payslips container: expected dict at data['payslips']",
                }
            )
        
        # If payslip_id is provided, return that specific payslip
        if payslip_id:
            payslip_id_str = str(payslip_id)
            
            if payslip_id_str not in payslips:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Payslip with ID '{payslip_id_str}' not found",
                    }
                )
            
            payslip = payslips[payslip_id_str]
            
            return json.dumps(
                {
                    "success": True,
                    "message": f"Retrieved payslip '{payslip_id_str}' for employee '{payslip.get('employee_id')}' in cycle '{payslip.get('cycle_id')}' with status '{payslip.get('status')}'",
                    "payslip": payslip,
                }
            )
        
        # Filter payslips based on provided parameters
        filtered_payslips = []
        
        for payslip in payslips.values():
            # Apply employee_id filter
            if employee_id is not None:
                if payslip.get("employee_id") != str(employee_id):
                    continue
            
            # Apply cycle_id filter
            if cycle_id is not None:
                if payslip.get("cycle_id") != str(cycle_id):
                    continue
            
            # Apply status filter
            if status is not None:
                if payslip.get("status") != status:
                    continue
            
            filtered_payslips.append(payslip)
        
        if not filtered_payslips:
            filter_desc = []
            if employee_id:
                filter_desc.append(f"employee_id='{employee_id}'")
            if cycle_id:
                filter_desc.append(f"cycle_id='{cycle_id}'")
            if status:
                filter_desc.append(f"status='{status}'")
            
            filter_str = " with " + ", ".join(filter_desc) if filter_desc else ""
            message = f"No payslips found{filter_str}" if filter_desc else "No payslips found"
            
            return json.dumps(
                {
                    "success": True,
                    "count": 0,
                    "payslips": [],
                    "message": message,
                }
            )
        
        return json.dumps(
            {
                "success": True,
                "count": len(filtered_payslips),
                "payslips": filtered_payslips,
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
                "name": "preview_payslip",
                "description": (
                    "Preview (retrieve) payslip(s) with flexible filtering options. "
                    "If payslip_id is provided, returns that specific payslip. "
                    "Otherwise, filters payslips by employee_id, cycle_id, and/or status. "
                    "If no filters are provided, returns all payslips. "
                    "Returns complete payslip details including payslip_id, employee_id, cycle_id, "
                    "net_pay_value, status, created_at, and last_updated. "
                    "This is typically used to verify payslips exist and check their status before "
                    "performing operations like releasing payslips. "
                    "Valid payslip statuses: 'draft', 'updated', 'released'."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "payslip_id": {
                            "type": "string",
                            "description": "Optional: Specific payslip ID to retrieve. If provided, other filters are ignored.",
                        },
                        "employee_id": {
                            "type": "string",
                            "description": "Optional: Filter payslips by employee ID.",
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "Optional: Filter payslips by payroll cycle ID.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional: Filter payslips by status ('draft', 'updated', or 'released').",
                        },
                    },
                    "required": [],
                },
            },
        }

