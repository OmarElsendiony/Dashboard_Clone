import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class GetPayslip(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        filters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Retrieve payslip records with optional filters.
        
        Args:
            data: The database dictionary containing all tables.
            filters: Optional JSON object with filter key-value pairs (AND logic).
                Supported fields: payslip_id, employee_id, cycle_id, status.
                status allowed values: 'draft', 'released', 'updated'.
        
        Returns:
            JSON string with entity_type, count, and results array.
        """
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if filters is not None and not isinstance(filters, dict):
            return json.dumps({"error": "filters must be a JSON object if provided"})

        # Access payslips table
        payslips = data.get("payslips", {})
        results = []
        effective_filters = filters or {}

        # Validate status filter if provided
        if "status" in effective_filters:
            allowed_statuses = ["draft", "released", "updated"]
            if effective_filters["status"] not in allowed_statuses:
                return json.dumps({
                    "error": f"Invalid status filter. Allowed values: {', '.join(allowed_statuses)}"
                })

        for record_id, record in payslips.items():
            if not isinstance(record, dict):
                continue

            match = True
            for key, value in effective_filters.items():
                if key == "payslip_id":
                    stored_id = record.get("payslip_id")
                    if str(record_id) != str(value) and str(stored_id) != str(value):
                        match = False
                        break
                else:
                    if record.get(key) != value:
                        match = False
                        break

            if match:
                result_record = {
                    "payslip_id": record.get("payslip_id", str(record_id)),
                    "employee_id": record.get("employee_id"),
                    "cycle_id": record.get("cycle_id"),
                    "net_pay_value": record.get("net_pay_value"),
                    "status": record.get("status"),
                    "created_at": record.get("created_at"),
                    "last_updated": record.get("last_updated"),
                }
                results.append(result_record)

        return json.dumps({
            "entity_type": "payslips",
            "count": len(results),
            "results": results,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_payslip",
                "description": (
                    "Retrieves payslip records from the system. "
                    "Optional filters allow narrowing results by payslip attributes."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filters": {
                            "type": "object",
                            "description": (
                                "Optional JSON object with filter key-value pairs (AND logic). "
                                "Supported fields: payslip_id, employee_id, cycle_id, status."
                            ),
                            "properties": {
                                "payslip_id": {
                                    "type": "string",
                                    "description": "The unique identifier of the payslip.",
                                },
                                "employee_id": {
                                    "type": "string",
                                    "description": "The employee ID associated with the payslip.",
                                },
                                "cycle_id": {
                                    "type": "string",
                                    "description": "The payroll cycle ID.",
                                },
                                "status": {
                                    "type": "string",
                                    "description": "The payslip status. Allowed values: 'draft', 'released', 'updated'.",
                                },
                            },
                        },
                    },
                    "required": [],
                },
            },
        }
