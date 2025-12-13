import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class RetrieveOnboardingPacket(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        filters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Retrieve onboarding packet/checklist records with optional filters.
        
        Args:
            data: The database dictionary containing all tables.
            filters: Optional JSON object with filter key-value pairs (AND logic).
                Supported fields: checklist_id, employee_id, status.
                status allowed values: 'pending', 'completed'.
        
        Returns:
            JSON string with entity_type, count, and results array.
        """
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if filters is not None and not isinstance(filters, dict):
            return json.dumps({"error": "filters must be a JSON object if provided"})

        # Access checklists table
        checklists = data.get("checklists", {})
        checklist_tasks = data.get("checklist_tasks", {})
        results = []
        effective_filters = filters or {}

        # Validate status filter if provided
        if "status" in effective_filters:
            allowed_statuses = ["pending", "completed"]
            if effective_filters["status"] not in allowed_statuses:
                return json.dumps({
                    "error": f"Invalid status filter. Allowed values: {', '.join(allowed_statuses)}"
                })

        for record_id, record in checklists.items():
            if not isinstance(record, dict):
                continue

            # Only include onboarding type checklists
            if record.get("checklist_type") != "onboarding":
                continue

            match = True
            for key, value in effective_filters.items():
                if key == "checklist_id":
                    stored_id = record.get("checklist_id")
                    if str(record_id) != str(value) and str(stored_id) != str(value):
                        match = False
                        break
                else:
                    if record.get(key) != value:
                        match = False
                        break

            if match:
                # Get associated tasks
                associated_tasks = []
                for task_id, task in checklist_tasks.items():
                    if task.get("checklist_id") == str(record_id) or task.get("checklist_id") == record.get("checklist_id"):
                        associated_tasks.append(task)

                result_record = {
                    "checklist_id": record.get("checklist_id", str(record_id)),
                    "checklist_type": record.get("checklist_type"),
                    "employee_id": record.get("employee_id"),
                    "status": record.get("status"),
                    "tasks": associated_tasks,
                    "created_at": record.get("created_at"),
                    "last_updated": record.get("last_updated"),
                }
                results.append(result_record)

        return json.dumps({
            "entity_type": "onboarding_checklists",
            "count": len(results),
            "results": results,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "retrieve_onboarding_packet",
                "description": (
                    "Retrieves onboarding packet/checklist records with their associated tasks. "
                    "Optional filters allow narrowing results by checklist attributes."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filters": {
                            "type": "object",
                            "description": (
                                "Optional JSON object with filter key-value pairs (AND logic). "
                                "Supported fields: checklist_id, employee_id, status."
                            ),
                            "properties": {
                                "checklist_id": {
                                    "type": "string",
                                    "description": "The unique identifier of the onboarding checklist.",
                                },
                                "employee_id": {
                                    "type": "string",
                                    "description": "The employee ID associated with the checklist.",
                                },
                                "status": {
                                    "type": "string",
                                    "description": "The checklist status. Allowed values: 'pending', 'completed'.",
                                },
                            },
                        },
                    },
                    "required": [],
                },
            },
        }
