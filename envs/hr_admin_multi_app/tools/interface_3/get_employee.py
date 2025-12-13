import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class GetEmployee(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        filters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Retrieve employee records with optional filters.
        
        Args:
            data: The database dictionary containing all tables.
            filters: Optional JSON object with filter key-value pairs (AND logic).
                Supported fields: employee_id, email, manager_id, department_id, status.
                status allowed values: 'active', 'inactive', 'on_leave', 'probation'.
        
        Returns:
            JSON string with entity_type, count, and results array.
        """
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if filters is not None and not isinstance(filters, dict):
            return json.dumps({"error": "filters must be a JSON object if provided"})

        # Access employees table
        employees = data.get("employees", {})
        results = []
        effective_filters = filters or {}

        # Validate status filter if provided
        if "status" in effective_filters:
            allowed_statuses = ["active", "inactive", "on_leave", "probation"]
            if effective_filters["status"] not in allowed_statuses:
                return json.dumps({
                    "error": f"Invalid status filter. Allowed values: {', '.join(allowed_statuses)}"
                })

        for record_id, record in employees.items():
            if not isinstance(record, dict):
                continue

            match = True
            for key, value in effective_filters.items():
                if key == "employee_id":
                    stored_id = record.get("employee_id")
                    if str(record_id) != str(value) and str(stored_id) != str(value):
                        match = False
                        break
                else:
                    if record.get(key) != value:
                        match = False
                        break

            if match:
                result_record = {
                    "employee_id": record.get("employee_id", str(record_id)),
                    "full_name": record.get("full_name"),
                    "email": record.get("email"),
                    "department_id": record.get("department_id"),
                    "manager_id": record.get("manager_id"),
                    "start_date": record.get("start_date"),
                    "base_salary": record.get("base_salary"),
                    "status": record.get("status"),
                    "tenure_months": record.get("tenure_months"),
                    "performance_rating": record.get("performance_rating"),
                    "location": record.get("location"),
                    "role": record.get("role"),
                    "flag_financial_counseling_recommended": record.get("flag_financial_counseling_recommended"),
                    "flag_potential_overtime_violation": record.get("flag_potential_overtime_violation"),
                    "flag_requires_payroll_review": record.get("flag_requires_payroll_review"),
                    "flag_high_offboard_risk": record.get("flag_high_offboard_risk"),
                    "flag_pending_settlement": record.get("flag_pending_settlement"),
                    "flag_requires_finance_approval": record.get("flag_requires_finance_approval"),
                    "created_at": record.get("created_at"),
                    "last_updated": record.get("last_updated"),
                }
                results.append(result_record)

        return json.dumps({
            "entity_type": "employees",
            "count": len(results),
            "results": results,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_employee",
                "description": (
                    "Retrieves employee records from the system. "
                    "Employees are individuals employed by the organization. "
                    "Optional filters allow narrowing results by employee attributes."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filters": {
                            "type": "object",
                            "description": (
                                "Optional JSON object with filter key-value pairs (AND logic). "
                                "Supported fields: employee_id, email, manager_id, department_id, status."
                            ),
                            "properties": {
                                "employee_id": {
                                    "type": "string",
                                    "description": "The unique identifier of the employee.",
                                },
                                "email": {
                                    "type": "string",
                                    "description": "The email address of the employee.",
                                },
                                "manager_id": {
                                    "type": "string",
                                    "description": "The ID of the employee's manager.",
                                },
                                "department_id": {
                                    "type": "string",
                                    "description": "The ID of the department the employee belongs to.",
                                },
                                "status": {
                                    "type": "string",
                                    "description": "The employment status. Allowed values: 'active', 'inactive', 'on_leave', 'probation'.",
                                },
                            },
                        },
                    },
                    "required": [],
                },
            },
        }

