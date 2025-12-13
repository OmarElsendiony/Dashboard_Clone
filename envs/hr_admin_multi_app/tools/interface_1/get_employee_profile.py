import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetEmployeeProfile(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        identifier: str,
        identifier_type: str = "employee_id",
    ) -> str:
        """
        Retrieve employee profile details and contract information by employee ID or email.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        employees = data.get("employees", {})
        contracts = data.get("contracts", {})

        if identifier_type == "employee_id":
            if str(identifier) in employees:
                employee_data = employees[str(identifier)].copy()
                
                # Fetch contract data for this employee
                contract_data = None
                for contract_id, contract in contracts.items():
                    if contract.get("employee_id") == str(identifier):
                        contract_data = contract.copy()
                        contract_data["contract_id"] = contract_id
                        break
                
                return json.dumps({
                    "success": True, 
                    "employee_data": employee_data,
                    "contract_data": contract_data
                })
            else:
                return json.dumps(
                    {"success": False, "error": f"Employee {identifier} not found"}
                )
        elif identifier_type == "email":
            for employee_id, employee in employees.items():
                if employee.get("email") == identifier:
                    employee_data = employee.copy()
                    
                    # Fetch contract data for this employee
                    contract_data = None
                    for contract_id, contract in contracts.items():
                        if contract.get("employee_id") == employee_id:
                            contract_data = contract.copy()
                            contract_data["contract_id"] = contract_id
                            break
                    
                    return json.dumps({
                        "success": True, 
                        "employee_data": employee_data,
                        "contract_data": contract_data
                    })
            return json.dumps(
                {"success": False, "error": f"Employee with email '{identifier}' not found"}
            )
        else:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid identifier_type '{identifier_type}'. Must be 'employee_id' or 'email'",
                }
            )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_employee_profile",
                "description": "Retrieves detailed information about an employee and their contract from the HR system. You can look up employees by their unique employee ID or by their email address. This function returns the employee's profile data including employee_id, manager_id, department_id, start_date, full_name, email, status (active/inactive/probation), tenure_months, performance_rating, base_salary, various flags (flag_financial_counseling_recommended, flag_potential_overtime_violation, flag_requires_payroll_review, flag_high_offboard_risk, flag_pending_settlement, flag_requires_finance_approval), and contract information including contract_id, document_url, is_terminated, and termination_date.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "identifier": {
                            "type": "string",
                            "description": "The value used to identify the employee. This can be either an employee ID or an email address. Required field.",
                        },
                        "identifier_type": {
                            "type": "string",
                            "description": "Specifies what type of identifier you're providing. The accepted values are 'employee_id' and 'email'. Use 'employee_id' when searching by employee ID, or 'email' when searching by email address. If not specified, defaults to 'employee_id'.",
                        },
                    },
                    "required": ["identifier"],
                },
            },
        }