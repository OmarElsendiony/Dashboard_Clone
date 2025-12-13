import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class GetCommission(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        filters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Retrieve commission (incentive) records with optional filters.
        
        Args:
            data: The database dictionary containing all tables.
            filters: Optional JSON object with filter key-value pairs (AND logic).
                Supported fields: earning_id, employee_id, cycle_id, status.
                status allowed values: 'pending', 'approved', 'rejected', 'require_justification'.
        
        Returns:
            JSON string with entity_type, count, and results array.
        """
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if filters is not None and not isinstance(filters, dict):
            return json.dumps({"error": "filters must be a JSON object if provided"})

        # Access payroll_earnings table and filter for incentive type
        payroll_earnings = data.get("payroll_earnings", {})
        results = []
        effective_filters = filters or {}

        # Validate status filter if provided
        if "status" in effective_filters:
            allowed_statuses = ["pending", "approved", "rejected", "require_justification"]
            if effective_filters["status"] not in allowed_statuses:
                return json.dumps({
                    "error": f"Invalid status filter. Allowed values: {', '.join(allowed_statuses)}"
                })

        for record_id, record in payroll_earnings.items():
            if not isinstance(record, dict):
                continue

            # Only include commission type
            if record.get("earning_type") != "commission":
                continue

            match = True
            for key, value in effective_filters.items():
                if key == "earning_id":
                    stored_id = record.get("earning_id")
                    if str(record_id) != str(value) and str(stored_id) != str(value):
                        match = False
                        break
                else:
                    if record.get(key) != value:
                        match = False
                        break

            if match:
                result_record = {
                    "earning_id": record.get("earning_id", str(record_id)),
                    "employee_id": record.get("employee_id"),
                    "cycle_id": record.get("cycle_id"),
                    "earning_type": record.get("earning_type"),
                    "amount": record.get("amount"),
                    "status": record.get("status"),
                    "created_at": record.get("created_at"),
                    "last_updated": record.get("last_updated"),
                }
                results.append(result_record)

        return json.dumps({
            "entity_type": "commission_earnings",
            "count": len(results),
            "results": results,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_commission",
                "description": (
                    "Retrieves commission earning records from the system. "
                    "Only returns earnings of type 'commission'. "
                    "Optional filters allow narrowing results by commission attributes."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filters": {
                            "type": "object",
                            "description": (
                                "Optional JSON object with filter key-value pairs (AND logic). "
                                "Supported fields: earning_id, employee_id, cycle_id, status."
                            ),
                            "properties": {
                                "earning_id": {
                                    "type": "string",
                                    "description": "The unique identifier of the earning.",
                                },
                                "employee_id": {
                                    "type": "string",
                                    "description": "The employee ID associated with the commission.",
                                },
                                "cycle_id": {
                                    "type": "string",
                                    "description": "The payroll cycle ID.",
                                },
                                "status": {
                                    "type": "string",
                                    "description": "The commission status. Allowed values: 'pending', 'approved', 'rejected', 'require_justification'.",
                                },
                            },
                        },
                    },
                    "required": [],
                },
            },
        }
