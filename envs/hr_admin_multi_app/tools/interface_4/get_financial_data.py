import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool

class GetFinancialData(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        type: str,
        employee_id: str,
        target_id: Optional[str] = None,
        earnings_filters: Optional[Dict[str, Optional[str]]] = None,
        payslip_filters: Optional[Dict[str, Optional[str]]] = None,
        payment_filters: Optional[Dict[str, Optional[str]]] = None,
        deduction_filters: Optional[Dict[str, Optional[str]]] = None
    ) -> str:
        """
        Get financial data based on type: 'deductions', 'payslips', 'payments', or 'payroll_earnings'.
        Returns filtered records based on the provided filters for the selected type.
        """
        employees = data.get("employees", {})
        payroll_cycles = data.get("payroll_cycles", {})
        deduction_rules = data.get("deduction_rules", {})
        payslips = data.get("payslips", {})
        
        # Validate required fields
        if not type:
            return json.dumps({
                "success": False,
                "error": "type is required"
            })
        
        if not employee_id:
            return json.dumps({
                "success": False,
                "error": "employee_id is required"
            })
        
        # Validate type
        valid_types = ["deductions", "payslips", "payments", "payroll_earnings"]
        if type not in valid_types:
            return json.dumps({
                "success": False,
                "error": f"Invalid type. Must be one of: {', '.join(valid_types)}"
            })
        
        # Validate employee exists
        if employee_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"employee_id '{employee_id}' does not reference a valid employee"
            })
        
        results = []
        
        if type == "deductions":
            deductions = data.get("deductions", {})
            filters = deduction_filters or {}
            
            # Validate cycle_id if provided
            if filters.get("cycle_id") is not None:
                if filters.get("cycle_id") not in payroll_cycles:
                    return json.dumps({
                        "success": False,
                        "error": f"cycle_id '{filters.get('cycle_id')}' does not reference a valid payroll cycle"
                    })
            
            # Validate deduction_rule_id if provided
            if filters.get("deduction_rule_id") is not None:
                if filters.get("deduction_rule_id") not in deduction_rules:
                    return json.dumps({
                        "success": False,
                        "error": f"deduction_rule_id '{filters.get('deduction_rule_id')}' does not reference a valid deduction rule"
                    })
            
            # Validate status enum if provided
            if filters.get("status") is not None:
                valid_statuses = ["valid", "invalid_limit_exceeded"]
                if filters.get("status") not in valid_statuses:
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid status for deductions. Must be one of: {', '.join(valid_statuses)}"
                    })
            
            for deduction_id, deduction in deductions.items():
                match = True
                
                # Always filter by employee_id
                if deduction.get("employee_id") != employee_id:
                    match = False
                if filters.get("cycle_id") is not None and deduction.get("cycle_id") != filters.get("cycle_id"):
                    match = False
                if filters.get("deduction_rule_id") is not None and deduction.get("deduction_rule_id") != filters.get("deduction_rule_id"):
                    match = False
                if filters.get("deduction_date") is not None and deduction.get("deduction_date") != filters.get("deduction_date"):
                    match = False
                if filters.get("status") is not None and deduction.get("status") != filters.get("status"):
                    match = False
                
                if match:
                    results.append(deduction)
        
        elif type == "payslips":
            payslips = data.get("payslips", {})
            filters = payslip_filters or {}
            
            # Validate cycle_id if provided
            if filters.get("cycle_id") is not None:
                if filters.get("cycle_id") not in payroll_cycles:
                    return json.dumps({
                        "success": False,
                        "error": f"cycle_id '{filters.get('cycle_id')}' does not reference a valid payroll cycle"
                    })
            
            # Validate status enum if provided
            if filters.get("status") is not None:
                valid_statuses = ["draft", "released", "updated"]
                if filters.get("status") not in valid_statuses:
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid status for payslips. Must be one of: {', '.join(valid_statuses)}"
                    })
            
            for payslip_id, payslip in payslips.items():
                match = True
                
                # Always filter by employee_id
                if payslip.get("employee_id") != employee_id:
                    match = False
                if filters.get("cycle_id") is not None and payslip.get("cycle_id") != filters.get("cycle_id"):
                    match = False
                if filters.get("status") is not None and payslip.get("status") != filters.get("status"):
                    match = False
                
                if match:
                    results.append(payslip)
        
        elif type == "payments":
            payments = data.get("payments", {})
            filters = payment_filters or {}
            
            # Validate source_payslip_id if provided
            if filters.get("source_payslip_id") is not None:
                if filters.get("source_payslip_id") not in payslips:
                    return json.dumps({
                        "success": False,
                        "error": f"source_payslip_id '{filters.get('source_payslip_id')}' does not reference a valid payslip"
                    })
            
            # Validate payment_method enum if provided
            if filters.get("payment_method") is not None:
                valid_methods = ["Bank Transfer", "Check"]
                if filters.get("payment_method") not in valid_methods:
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid payment_method. Must be one of: {', '.join(valid_methods)}"
                    })
            
            # Validate status enum if provided
            if filters.get("status") is not None:
                valid_statuses = ["pending", "completed", "failed"]
                if filters.get("status") not in valid_statuses:
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid status for payments. Must be one of: {', '.join(valid_statuses)}"
                    })
            
            for payment_id, payment in payments.items():
                match = True
                
                # Always filter by employee_id
                if payment.get("employee_id") != employee_id:
                    match = False
                if filters.get("payment_method") is not None and payment.get("payment_method") != filters.get("payment_method"):
                    match = False
                if filters.get("payment_date") is not None and payment.get("payment_date") != filters.get("payment_date"):
                    match = False
                if filters.get("source_payslip_id") is not None and payment.get("source_payslip_id") != filters.get("source_payslip_id"):
                    match = False
                if filters.get("status") is not None and payment.get("status") != filters.get("status"):
                    match = False
                
                if match:
                    results.append(payment)
        
        elif type == "payroll_earnings":
            payroll_earnings = data.get("payroll_earnings", {})
            filters = earnings_filters or {}
            
            # Validate cycle_id if provided (though earnings don't have cycle_id, we'll just ignore it)
            # Actually, payroll_earnings don't have cycle_id, so we can skip that validation
            
            # Validate earning_type enum if provided
            if filters.get("earning_type") is not None:
                valid_types = ["bonus", "incentive", "allowance", "payroll input", "commission"]
                if filters.get("earning_type") not in valid_types:
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid earning_type. Must be one of: {', '.join(valid_types)}"
                    })
            
            # Validate status enum if provided
            if filters.get("status") is not None:
                valid_statuses = ["pending", "approved", "rejected", "require_justification"]
                if filters.get("status") not in valid_statuses:
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid status for payroll_earnings. Must be one of: {', '.join(valid_statuses)}"
                    })
            
            for earning_id, earning in payroll_earnings.items():
                match = True
                
                # Always filter by employee_id
                if earning.get("employee_id") != employee_id:
                    match = False
                if filters.get("earning_type") is not None and earning.get("earning_type") != filters.get("earning_type"):
                    match = False
                if filters.get("status") is not None and earning.get("status") != filters.get("status"):
                    match = False
                
                if match:
                    results.append(earning)
        
        return json.dumps({
            "success": True,
            "type": type,
            "count": len(results),
            "data": results
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_financial_data",
                "description": "Get financial data based on type: 'deductions', 'payslips', 'payments', or 'payroll_earnings'. Returns all records for the employee if no filters are provided, or filtered records if filters are provided. If type is 'deductions' then deduction_filters can have: cycle_id, deduction_rule_id, deduction_date, status. If type is 'payslips' then payslip_filters can have: cycle_id, status. If type is 'payments' then payment_filters can have: payment_method, payment_date, source_payslip_id, status. If type is 'payroll_earnings' then earnings_filters can have: earning_type, cycle_id, status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": "Type of financial data to retrieve: 'deductions', 'payslips', 'payments', or 'payroll_earnings' (required)",
                            "enum": ["deductions", "payslips", "payments", "payroll_earnings"]
                        },
                        "employee_id": {
                            "type": "string",
                            "description": "Employee ID (required)"
                        },
                        "target_id": {
                            "type": "string",
                            "description": "Target ID (optional)"
                        },
                        "earnings_filters": {
                            "type": "object",
                            "description": "Filters for payroll_earnings (optional). If not provided, returns all earnings for the employee.",
                            "properties": {
                                "earning_type": {
                                    "type": "string",
                                    "description": "Earning type: bonus, incentive, allowance, payroll input, commission (optional)",
                                    "enum": ["bonus", "incentive", "allowance", "payroll input", "commission"]
                                },
                                "cycle_id": {
                                    "type": "string",
                                    "description": "Cycle ID (optional, not applicable for earnings)"
                                },
                                "status": {
                                    "type": "string",
                                    "description": "Status: pending, approved, rejected, require_justification (optional)",
                                    "enum": ["pending", "approved", "rejected", "require_justification"]
                                }
                            }
                        },
                        "payslip_filters": {
                            "type": "object",
                            "description": "Filters for payslips (optional). If not provided, returns all payslips for the employee.",
                            "properties": {
                                "cycle_id": {
                                    "type": "string",
                                    "description": "Payroll cycle ID (optional)"
                                },
                                "status": {
                                    "type": "string",
                                    "description": "Status: draft, released, updated (optional)",
                                    "enum": ["draft", "released", "updated"]
                                }
                            }
                        },
                        "payment_filters": {
                            "type": "object",
                            "description": "Filters for payments (optional). If not provided, returns all payments for the employee.",
                            "properties": {
                                "payment_method": {
                                    "type": "string",
                                    "description": "Payment method: Bank Transfer, Check (optional)",
                                    "enum": ["Bank Transfer", "Check"]
                                },
                                "payment_date": {
                                    "type": "string",
                                    "description": "Payment date (optional)"
                                },
                                "source_payslip_id": {
                                    "type": "string",
                                    "description": "Source payslip ID (optional)"
                                },
                                "status": {
                                    "type": "string",
                                    "description": "Status: pending, completed, failed (optional)",
                                    "enum": ["pending", "completed", "failed"]
                                }
                            }
                        },
                        "deduction_filters": {
                            "type": "object",
                            "description": "Filters for deductions (optional). If not provided, returns all deductions for the employee.",
                            "properties": {
                                "cycle_id": {
                                    "type": "string",
                                    "description": "Payroll cycle ID (optional)"
                                },
                                "deduction_rule_id": {
                                    "type": "string",
                                    "description": "Deduction rule ID (optional)"
                                },
                                "deduction_date": {
                                    "type": "string",
                                    "description": "Deduction date (optional)"
                                },
                                "status": {
                                    "type": "string",
                                    "description": "Status: valid, invalid_limit_exceeded (optional)",
                                    "enum": ["valid", "invalid_limit_exceeded"]
                                }
                            }
                        }
                    },
                    "required": ["type", "employee_id"]
                }
            }
        }
