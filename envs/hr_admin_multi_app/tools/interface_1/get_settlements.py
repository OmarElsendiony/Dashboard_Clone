import json
from typing import Any, Dict, Optional, Union
from tau_bench.envs.tool import Tool


class GetSettlements(Tool):
    """
    Retrieve or search for finance settlements with flexible filters.
    - Returns ALL settlements when no filters are provided.
    - Applies all provided filters using AND logic.
    - Safe handling of ID comparisons (cast to str), booleans, and numeric ranges.
    - Datetime prefix matches for timestamps.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        settlement_id: Optional[str] = None,
        employee_id: Optional[str] = None,
        is_cleared: Optional[bool] = None,
        min_amount: Optional[Union[int, float]] = None,
        max_amount: Optional[Union[int, float]] = None,
        created_at: Optional[str] = None,
        last_updated: Optional[str] = None,
    ) -> str:
        """
        Return a JSON string:
          {"success": True, "settlements": [...]} on success
          {"success": False, "error": "..."} on error
        """

        # --- Basic input validation ---
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        settlements_dict = data.get("finance_settlements", {})
        if not isinstance(settlements_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid settlements container: expected dict at data['finance_settlements']",
                }
            )

        # --- Validate numeric ranges ---
        if min_amount is not None:
            try:
                min_amount = float(min_amount)
                if min_amount < 0:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "Invalid min_amount: must be non-negative",
                        }
                    )
            except (TypeError, ValueError):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid min_amount: '{min_amount}' must be a number",
                    }
                )

        if max_amount is not None:
            try:
                max_amount = float(max_amount)
                if max_amount < 0:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "Invalid max_amount: must be non-negative",
                        }
                    )
            except (TypeError, ValueError):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid max_amount: '{max_amount}' must be a number",
                    }
                )

        if min_amount is not None and max_amount is not None and min_amount > max_amount:
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid range: min_amount cannot be greater than max_amount",
                }
            )

        # --- Validate boolean ---
        if is_cleared is not None and not isinstance(is_cleared, bool):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid is_cleared value: '{is_cleared}'. Must be a boolean (true or false)",
                }
            )

        # --- Collect active filters (keep None out) ---
        filters = {
            "settlement_id": settlement_id,
            "employee_id": employee_id,
            "is_cleared": is_cleared,
            "min_amount": min_amount,
            "max_amount": max_amount,
            "created_at": created_at,
            "last_updated": last_updated,
        }
        active_filters = {k: v for k, v in filters.items() if v is not None}

        # Start with all settlements (dict copy to avoid mutating original rows)
        all_settlements = [
            s.copy() for s in settlements_dict.values() if isinstance(s, dict)
        ]

        # If no filters, return everything
        if not active_filters:
            return json.dumps({"success": True, "settlements": all_settlements})

        # --- Apply filters incrementally (AND logic) ---
        results = all_settlements

        # ID / FK filters (compare as string)
        if settlement_id is not None:
            sid = str(settlement_id)
            results = [s for s in results if s.get("settlement_id") == sid]

        if employee_id is not None:
            eid = str(employee_id)
            results = [s for s in results if s.get("employee_id") == eid]

        # Boolean filter
        if is_cleared is not None:
            results = [s for s in results if s.get("is_cleared") == is_cleared]

        # Numeric range filters
        if min_amount is not None:
            results = [
                s
                for s in results
                if "amount" in s
                and s["amount"] is not None
                and float(s["amount"]) >= min_amount
            ]

        if max_amount is not None:
            results = [
                s
                for s in results
                if "amount" in s
                and s["amount"] is not None
                and float(s["amount"]) <= max_amount
            ]

        # Datetime prefix filters (e.g., "2024-01-05")
        if created_at is not None:
            results = [
                s for s in results if s.get("created_at", "").startswith(created_at)
            ]

        if last_updated is not None:
            results = [
                s for s in results if s.get("last_updated", "").startswith(last_updated)
            ]

        return json.dumps({"success": True, "settlements": results})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """
        Tool schema for function-calling.
        """
        return {
            "type": "function",
            "function": {
                "name": "get_settlements",
                "description": "Retrieves finance settlements from the HR system based on search criteria. A settlement represents financial obligations or dues associated with employees, typically used during offboarding processes to track pending payments or receivables. When called with no parameters, returns all settlements in the system. When called with parameters, filters and returns only matching settlements. You can combine multiple filters to narrow down results. All filters support AND logic (all conditions must match).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "settlement_id": {
                            "type": "string",
                            "description": "The unique identifier for a specific settlement. Performs exact match. ",
                        },
                        "employee_id": {
                            "type": "string",
                            "description": "The employee ID associated with the settlement. Performs exact match. ",
                        },
                        "is_cleared": {
                            "type": "boolean",
                            "description": "Filters by settlement clearance status. true = settlement has been cleared/resolved. false = settlement is still pending. Use this to find pending or completed settlements.",
                        },
                        "min_amount": {
                            "type": "number",
                            "description": "Minimum settlement amount (inclusive). Filters settlements with amount >= this value. ",
                        },
                        "max_amount": {
                            "type": "number",
                            "description": "Maximum settlement amount (inclusive). Filters settlements with amount <= this value. ",
                        },
                        "created_at": {
                            "type": "string",
                            "description": "Filters settlements by creation date/time. Performs prefix matching on ISO datetime format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS). ",
                        },
                        "last_updated": {
                            "type": "string",
                            "description": "Filters settlements by last update date/time. Performs prefix matching on ISO datetime format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS). ",
                        },
                    },
                    "required": [],
                },
            },
        }

