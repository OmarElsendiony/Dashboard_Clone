import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool


class GetDeductionData(Tool):
    """
    Retrieve deduction data for an employee, including deductions and deduction rules.
    Can be filtered by deduction_type.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        target: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Retrieve deduction rules or data if filters is provided.
        
        Args:
            data: Dictionary containing deductions, deduction_rules, and employees
            target: 'deduction_rules' or 'deduction_data' to get deductions with rules
            filters: Optional dictionary with keys:
            
        Returns:
            JSON string with success status and list of deduction records with rule details
        """
        
        # Validate data format
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format: 'data' must be a dict"}
            )
        deduction_rules = data.get("deduction_rules", {})
        if not isinstance(deduction_rules, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid deduction_rules container: expected dict at data['deduction_rules']",
                }
            )
        if target == "deduction_data":
            filters = json.loads(filters) if isinstance(filters, str) else filters
            employee_id = None
            deduction_type = None
            if filters:
                deduction_type = filters.get("deduction_type")
                employee_id = filters.get("employee_id")
            deductions = data.get("deductions", {})
            if not isinstance(deductions, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Invalid deductions container: expected dict at data['deductions']",
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
            
            # Validate required fields
            if not employee_id:
                return json.dumps(
                    {"success": False, "error": "employee_id is required"}
            )
        
            employee_id_str = str(employee_id)
            
            # Validate employee exists
            if employee_id_str not in employees:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Employee with ID '{employee_id_str}' not found",
                    }
                )
        
            employee = employees[employee_id_str]
            
            # Valid deduction types
            valid_deduction_types = [
                "benefit_contribution",
                "loan",
                "retirement",
                "insurance",
                "tax",
                "garnishment",
                "repayment_of_overpayment",
            ]
        
            # Validate deduction_type if provided
            if deduction_type and deduction_type not in valid_deduction_types:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid deduction_type value: '{deduction_type}'. Must be one of {valid_deduction_types}",
                    }
                )
        
            # Build a mapping of rule_id to rule details
            rules_by_id = {}
            for rule in deduction_rules.values():
                rules_by_id[rule.get("rule_id")] = rule
            
            # Collect deductions for the employee
            result_deductions = []
            
            for deduction in deductions.values():
                if deduction.get("employee_id") == employee_id_str:
                    # Get the associated rule
                    rule_id = deduction.get("deduction_rule_id")
                    rule = rules_by_id.get(rule_id, {})
                    
                    # Filter by deduction_type if provided
                    if deduction_type:
                        if rule.get("deduction_type") != deduction_type:
                            continue
                    
                    # Build the result with deduction and rule information
                    deduction_with_rule = {
                        "deduction_id": deduction.get("deduction_id"),
                        "employee_id": deduction.get("employee_id"),
                        "cycle_id": deduction.get("cycle_id"),
                        "deduction_rule_id": deduction.get("deduction_rule_id"),
                        "amount": deduction.get("amount"),
                        "deduction_date": deduction.get("deduction_date"),
                        "status": deduction.get("status"),
                        "created_at": deduction.get("created_at"),
                        "last_updated": deduction.get("last_updated"),
                        "deduction_rule": {
                            "rule_id": rule.get("rule_id"),
                            "deduction_type": rule.get("deduction_type"),
                            "max_percent_of_net_pay": rule.get("max_percent_of_net_pay"),
                            "status": rule.get("status"),
                        } if rule else None,
                    }
                    
                    result_deductions.append(deduction_with_rule)
            
            # Sort by deduction_date (most recent first)
            result_deductions.sort(
                key=lambda x: x.get("deduction_date", ""),
                reverse=True
            )
            
            message = f"Found {len(result_deductions)} deduction(s) for employee '{employee.get('full_name')}' ({employee_id_str})"
            if deduction_type:
                message += f" with deduction_type '{deduction_type}'"
            
            return json.dumps(
                {
                    "success": True,
                    "message": message,
                    "deductions": result_deductions,
                    "count": len(result_deductions),
                }
            )
        elif target == "deduction_rules":
            # Return all deduction rules
            all_rules = list(deduction_rules.values())
            return json.dumps(
                {
                    "success": True,
                    "message": f"Found {len(all_rules)} deduction rule(s)",
                    "deduction_rules": all_rules,
                    "count": len(all_rules),
                }
            )
        else:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid target '{target}'. Must be 'deduction_data' or 'deduction_rules'",
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
                "name": "get_deduction_data",
                "description": (
                    "Retrieve deduction rules or data for an employee, depending on the target specified. "
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "description": "Specify whether to retrieve 'deduction_rules' or 'deduction_data' for the employee (required)"},
                        "filters": {
                            "type": "object",
                            "description": "Optional filters to apply when retrieving deduction data. deduction_type and employee_id(required).",
                            "properties": {
                                "deduction_type": {
                                    "type": "string",
                                    "description": "Type of deduction to filter by (optional). Valid types: benefit_contribution, loan, retirement, insurance, tax, garnishment, repayment_of_overpayment",
                                },
                                "employee_id": {
                                    "type": "string",
                                    "description": "ID of the employee to filter deductions for (required when target is 'deduction_data')",
                                },
                            },
                            
                            }
                        
                        },
                    "required": ["target"]
                    }
                }
            }