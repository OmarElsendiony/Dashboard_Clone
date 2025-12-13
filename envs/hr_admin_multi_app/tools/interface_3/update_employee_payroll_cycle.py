import json
from typing import Any, Dict

from tau_bench.envs.tool import Tool


class UpdateEmployeePayrollCycle(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        cycle_id: str,
        updates_fields: Dict[str, Any],
    ) -> str:
        """
        Update an existing payroll cycle.
        
        Args:
            data: The database dictionary containing all tables.
            cycle_id: The ID of the payroll cycle to update (required).
            updates_fields: JSON object containing fields to update (required).
                Supported fields: start_date, end_date, frequency, status.
                status allowed values: 'open', 'closed'.
        
        Returns:
            JSON string with the updated payroll cycle record.
        """
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not cycle_id:
            return json.dumps({"error": "Missing required parameter: cycle_id is required"})
        if not updates_fields or not isinstance(updates_fields, dict):
            return json.dumps({"error": "Missing required parameter: updates_fields must be a JSON object"})

        cycle_id = str(cycle_id)
        payroll_cycles = data.get("payroll_cycles", {})

        if cycle_id not in payroll_cycles:
            return json.dumps({"error": f"Payroll cycle with ID '{cycle_id}' not found"})

        cycle = payroll_cycles[cycle_id]

        # Validate status if being updated
        if "status" in updates_fields:
            allowed_statuses = ["open", "closed"]
            if updates_fields["status"] not in allowed_statuses:
                return json.dumps({
                    "error": f"Invalid status. Allowed values: {', '.join(allowed_statuses)}"
                })

        # Allowed fields to update
        allowed_fields = ["start_date", "end_date", "frequency", "status"]

        for key, value in updates_fields.items():
            if key in allowed_fields:
                cycle[key] = value

        cycle["last_updated"] = "2025-11-16T23:59:00"

        return json.dumps(cycle)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_employee_payroll_cycle",
                "description": (
                    "Updates an existing payroll cycle with the provided fields. "
                    "Use this to change cycle dates, frequency, or status."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cycle_id": {
                            "type": "string",
                            "description": "The ID of the payroll cycle to update (required).",
                        },
                        "updates_fields": {
                            "type": "object",
                            "description": (
                                "JSON object containing fields to update (required). "
                                "Supported fields: start_date, end_date, frequency, status."
                            ),
                            "properties": {
                                "start_date": {
                                    "type": "string",
                                    "description": "The start date in format (YYYY-MM-DD).",
                                },
                                "end_date": {
                                    "type": "string",
                                    "description": "The end date in format (YYYY-MM-DD).",
                                },
                                "frequency": {
                                    "type": "string",
                                    "description": "The payroll frequency.",
                                },
                                "status": {
                                    "type": "string",
                                    "description": "The cycle status. Allowed values: 'open', 'closed'.",
                                },
                            },
                        },
                    },
                    "required": ["cycle_id", "updates_fields"],
                },
            },
        }
