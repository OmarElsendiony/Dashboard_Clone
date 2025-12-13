import json
from typing import Any, Dict

from tau_bench.envs.tool import Tool


class DeactivatePayrollIntegration(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        cycle_id: str,
    ) -> str:
        """
        Deactivate a payroll cycle integration by closing it.
        
        Args:
            data: The database dictionary containing all tables.
            cycle_id: The ID of the payroll cycle to deactivate (required).
        
        Returns:
            JSON string with the deactivated payroll cycle record.
        """
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not cycle_id:
            return json.dumps({"error": "Missing required parameter: cycle_id is required"})

        cycle_id = str(cycle_id)
        payroll_cycles = data.get("payroll_cycles", {})

        if cycle_id not in payroll_cycles:
            return json.dumps({"error": f"Payroll cycle with ID '{cycle_id}' not found"})

        cycle = payroll_cycles[cycle_id]
        
        if cycle.get("status") == "closed":
            return json.dumps({"error": f"Payroll cycle '{cycle_id}' is already closed"})

        cycle["status"] = "closed"
        cycle["last_updated"] = "2025-12-12T12:00:00"

        return json.dumps(cycle)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "deactivate_payroll_integration",
                "description": (
                    "Deactivates a payroll cycle integration by setting its status to 'closed'. "
                    "Use this when a payroll cycle is complete and no longer active."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cycle_id": {
                            "type": "string",
                            "description": "The ID of the payroll cycle to deactivate (required).",
                        },
                    },
                    "required": ["cycle_id"],
                },
            },
        }
