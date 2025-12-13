import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetPayrollData(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        entity_type: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Retrieve payroll-related data (cycles, inputs, or earnings) with optional filters.
        """
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if entity_type not in ["payroll_cycles", "payroll_inputs", "payroll_earnings"]:
            return json.dumps(
                {
                    "error": "Invalid entity_type. Allowed values: "
                    "'payroll_cycles', 'payroll_inputs', 'payroll_earnings'"
                }
            )

        if filters is not None and not isinstance(filters, dict):
            return json.dumps({"error": "filters must be a JSON object if provided"})

        id_field_map: Dict[str, str] = {
            "payroll_cycles": "cycle_id",
            "payroll_inputs": "input_id",
            "payroll_earnings": "earning_id",
        }

        table = data.get(entity_type, {})
        results = []
        id_field = id_field_map[entity_type]

        # Special handling for payroll_cycles filtered by employee_id
        employee_id_for_cycles: Optional[str] = None
        effective_filters: Dict[str, Any] = {}

        if entity_type == "payroll_cycles" and filters:
            # Separate employee_id filter for cycles (derived via inputs/earnings)
            employee_id_for_cycles = filters.get("employee_id")
            effective_filters = {k: v for k, v in filters.items() if k != "employee_id"}
        else:
            effective_filters = filters or {}

        # Convert ID values in filters to strings for consistent comparison
        if effective_filters:
            id_filter_fields = ["cycle_id", "input_id", "earning_id", "employee_id"]
            for field in id_filter_fields:
                if field in effective_filters and effective_filters[field] is not None:
                    effective_filters[field] = str(effective_filters[field])
        
        if employee_id_for_cycles is not None:
            employee_id_for_cycles = str(employee_id_for_cycles)

        allowed_cycle_ids_for_employee = None
        if entity_type == "payroll_cycles" and employee_id_for_cycles:
            allowed_cycle_ids_for_employee = set()

            for _input_id, input_record in data.get("payroll_inputs", {}).items():
                if input_record.get("employee_id") == employee_id_for_cycles:
                    cycle_id = input_record.get("cycle_id")
                    if cycle_id:
                        allowed_cycle_ids_for_employee.add(str(cycle_id))

            for _earning_id, earning_record in data.get("payroll_earnings", {}).items():
                if earning_record.get("employee_id") == employee_id_for_cycles:
                    cycle_id = earning_record.get("cycle_id")
                    if cycle_id:
                        allowed_cycle_ids_for_employee.add(str(cycle_id))

        for record_id, record in table.items():
            if not isinstance(record, dict):
                # Skip malformed records
                continue

            # Apply derived employee_id filter for payroll_cycles if present
            if (
                entity_type == "payroll_cycles"
                and allowed_cycle_ids_for_employee is not None
                and str(record_id) not in allowed_cycle_ids_for_employee
            ):
                continue

            match = True
            for key, value in effective_filters.items():
                # Support filtering by ID field either via stored field or record key
                if key == id_field:
                    stored_id = record.get(id_field)
                    if str(record_id) != str(value) and str(stored_id) != str(value):
                        match = False
                        break
                else:
                    if record.get(key) != value:
                        match = False
                        break

            if match:
                result_record = record.copy()
                if id_field not in result_record:
                    result_record[id_field] = str(record_id)
                results.append(result_record)

        return json.dumps(
            {
                "entity_type": entity_type,
                "count": len(results),
                "results": results,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_payroll_data",
                "description": (
                    "Retrieves payroll-related data from the HR system. "
                    "Supports three entity types: "
                    "'payroll_cycles' (payroll cycle definitions), "
                    "'payroll_inputs' (per-employee input records like hours and allowances), "
                    "and 'payroll_earnings' (per-employee earnings such as bonuses or incentives). "
                    "Optional filters allow narrowing results by ID, status, dates, or employee. "
                    "For 'payroll_cycles', you can also filter by employee_id to return only cycles "
                    "that have inputs or earnings for that employee."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entity_type": {
                            "type": "string",
                            "description": (
                                "Type of payroll data to retrieve. "
                                "Allowed values: 'payroll_cycles', 'payroll_inputs', 'payroll_earnings'."
                            ),
                        },
                        "filters": {
                            "type": "object",
                            "description": (
                                "Optional filters as a JSON object with key-value pairs (AND logic). "
                                "Exact matching is used for all filters. "
                                "For 'payroll_cycles', supported filters include: "
                                "cycle_id (string), status (string; allowed values: 'open', 'closed'), "
                                "start_date (string; date in format (YYYY-MM-DD)), "
                                "end_date (string; date in format (YYYY-MM-DD)), "
                                "employee_id (string; returns only cycles that have inputs or earnings for this employee). "
                                "For 'payroll_inputs', supported filters include: "
                                "input_id (string), employee_id (string), cycle_id (string), "
                                "status (string; allowed values: 'pending', 'review'). "
                                "For 'payroll_earnings', supported filters include: "
                                "earning_id (string), employee_id (string), cycle_id (string), "
                                "status (string; allowed values: 'pending', 'approved', 'rejected', 'require_justification')."
                            ),
                        },
                    },
                    "required": ["entity_type"],
                },
            },
        }
