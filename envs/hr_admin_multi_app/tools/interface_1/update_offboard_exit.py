import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdateOffboardExit(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        exit_case_id: str,
        exit_clearance_status: Optional[str] = None,
        reason: Optional[str] = None,
        exit_date: Optional[str] = None,
    ) -> str:
        """
        Update an exit case record for an offboarding employee.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        exit_cases = data.get("exit_cases", {})

        # Validate exit case exists
        if str(exit_case_id) not in exit_cases:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Exit case {exit_case_id} not found",
                }
            )

        exit_case = exit_cases[str(exit_case_id)]
        current_time = "2025-11-16T23:59:00"

        # Update exit_clearance_status if provided
        if exit_clearance_status is not None:
            # Valid statuses based on schema: "pending" (default) or "cleared" (SOP 18)
            valid_clearance_statuses = ["pending", "cleared"]
            if exit_clearance_status not in valid_clearance_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid exit_clearance_status '{exit_clearance_status}'. Must be one of {valid_clearance_statuses}",
                    }
                )
            exit_case["exit_clearance_status"] = exit_clearance_status

        # Update reason if provided
        if reason is not None:
            valid_reasons = [
                "misconduct",
                "security_breach",
                "policy_violation",
                "voluntary_resignation",
                "layoff",
            ]
            if reason not in valid_reasons:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid reason '{reason}'. Must be one of {valid_reasons}",
                    }
                )
            exit_case["reason"] = reason

        # Update exit_date if provided
        if exit_date is not None:
            exit_case["exit_date"] = exit_date

        exit_case["last_updated"] = current_time

        return json.dumps(
            {
                "success": True,
                "message": f"Exit case {exit_case_id} updated successfully",
                "exit_case_data": exit_case.copy(),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_offboard_exit",
                "description": "Updates an exit case record for an offboarding employee. This function can update the exit clearance status (e.g., from 'pending' to 'cleared'), the reason for exit, and the exit date. The exit_clearance_status is typically updated to 'cleared' after all exit clearance procedures are completed, including asset returns and finance settlements",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "exit_case_id": {
                            "type": "string",
                            "description": "The unique identifier of the exit case to update. Required field.",
                        },
                        "exit_clearance_status": {
                            "type": "string",
                            "description": "The clearance status of the exit case. Valid values are 'pending' or 'cleared'. Typically updated to 'cleared' once all exit procedures are completed. Optional field.",
                        },
                        "reason": {
                            "type": "string",
                            "description": "The reason for employee exit. Valid values are 'misconduct', 'security_breach', 'policy_violation', 'voluntary_resignation', or 'layoff'. Optional field.",
                        },
                        "exit_date": {
                            "type": "string",
                            "description": "The exit date of the employee in YYYY-MM-DD format. Optional field.",
                        },
                    },
                    "required": ["exit_case_id"],
                },
            },
        }
