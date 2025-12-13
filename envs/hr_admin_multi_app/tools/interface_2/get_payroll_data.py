import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class GetPayrollData(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        entity_type: str,
        filters: Dict[str, Any],
    ) -> str:
        """
        Get financial data based on type: 'payslips' or 'payroll_earnings'.
        Returns filtered records based on payslip_id, earning_id, employee_id, cycle_id (if applicable), and status.
        filters: {"payslip_id": str (optional), "earning_id": str (optional), "employee_id": str (required), "cycle_id": str (optional)}
        """
        employees = data.get("employees", {})
        results = []
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        if entity_type not in ["payslips", "payroll_earnings"]:
            return json.dumps({
                "success": False,
                "error": f"entity_type '{entity_type}' is not valid. Must be 'payslips' or 'payroll_earnings'."
            })
        employee_id = filters.get("employee_id")

        if employee_id and employee_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"employee_id '{employee_id}' does not reference a valid employee"
            })
        if entity_type == "payslips":
            payslips = data.get("payslips", {})
            for ps_id, payslip in payslips.items():
                if employee_id and payslip.get("employee_id") != employee_id:
                    continue
                if "payslip_id" in filters and ps_id != filters["payslip_id"]:
                    continue
                if "cycle_id" in filters and payslip.get("cycle_id") != filters["cycle_id"]:
                    continue
                if "status" in filters and payslip.get("status") != filters["status"]:
                    continue
                results.append(payslip.copy())
        elif entity_type == "payroll_earnings":
            payroll_earnings = data.get("payroll_earnings", {})
            for earning_id, earning in payroll_earnings.items():
                if employee_id and earning.get("employee_id") != employee_id:
                    continue
                if "earning_id" in filters and earning_id != filters["earning_id"]:
                    continue
                if "status" in filters and earning.get("status") != filters["status"]:
                    continue
                results.append(earning.copy())
        return json.dumps({"success": True, "count": len(results), "data": results})
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_payroll_data",
                "description": "Get financial data based on entity_type: 'payslips', or 'payroll_earnings'. Returns filtered records based on payslip_id, earning_id, employee_id, cycle_id (if applicable), and status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entity_type": {
                            "entity_type": "string",
                            "description": "Type of financial data to retrieve: 'payslips', or 'payroll_earnings' (required)",
                            "enum": ["deductions", "payslips", "payments", "payroll_earnings"]
                        },
                        "filters": {
                            "type": "object",
                            "description": "Filters to apply to the data retrieval",
                            "properties": {
                                "payslip_id": {
                                    "type": "string",
                                    "description": "Payslip ID (optional, applicable for payslips)"
                                },
                                "earning_id": {
                                    "type": "string",
                                    "description": "Earning ID (optional, applicable for payroll earnings)"
                                },
                                "employee_id": {
                                    "type": "string",
                                    "description": "Employee ID (required)"
                                },
                                "cycle_id": {
                                    "type": "string",
                                    "description": "Payroll cycle ID (optional, applicable for deductions and payslips)"
                                },
                            }
                        }
                        
                    },
                    "required": ["entity_type"]
                }
            }
        }