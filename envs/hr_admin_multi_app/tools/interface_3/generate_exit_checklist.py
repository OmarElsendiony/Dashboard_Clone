import json
from typing import Any, Dict

from tau_bench.envs.tool import Tool


class GenerateExitChecklist(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
    ) -> str:
        """
        Generate an exit checklist for an offboarding employee by retrieving their
        offboarding checklist and associated tasks from the database.
        
        Args:
            data: The database dictionary containing all tables.
            employee_id: The ID of the departing employee (required).
        
        Returns:
            JSON string with the exit checklist including all tasks, outstanding assets, 
            and pending settlements.
        """
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not employee_id:
            return json.dumps({"error": "Missing required parameter: employee_id is required"})

        employee_id = str(employee_id)
        employees = data.get("employees", {})
        exit_cases = data.get("exit_cases", {})
        checklists = data.get("checklists", {})
        checklist_tasks = data.get("checklist_tasks", {})
        employee_assets = data.get("employee_assets", {})
        finance_settlements = data.get("finance_settlements", {})

        # Validate employee exists
        if employee_id not in employees:
            return json.dumps({"error": f"Employee with ID '{employee_id}' not found"})

        employee = employees[employee_id]

        # Find the exit case for this employee
        exit_case = None
        exit_case_id = None
        for case_id, case in exit_cases.items():
            if case.get("employee_id") == employee_id:
                exit_case = case
                exit_case_id = case_id
                break

        if not exit_case:
            return json.dumps({
                "error": f"No exit case found for employee '{employee_id}'. Use initiate_offboarding first."
            })

        # Find the offboarding checklist for this employee
        offboarding_checklist = None
        offboarding_checklist_id = None
        for checklist_id, checklist in checklists.items():
            if (checklist.get("employee_id") == employee_id and 
                checklist.get("checklist_type") == "offboarding"):
                offboarding_checklist = checklist
                offboarding_checklist_id = checklist_id
                break

        if not offboarding_checklist:
            return json.dumps({
                "error": f"No offboarding checklist found for employee '{employee_id}'. Use initiate_offboarding first."
            })

        # Retrieve all tasks associated with this offboarding checklist
        checklist_items = []
        for task_id, task in checklist_tasks.items():
            if task.get("checklist_id") == offboarding_checklist_id:
                checklist_items.append({
                    "task_id": task_id,
                    "task": task.get("name"),
                    "status": task.get("status"),
                    "due_date": task.get("due_date"),
                    "assigned_manager_id": task.get("assigned_manager_id"),
                    "required": True,
                })

        # Check for outstanding assets
        outstanding_assets = []
        for asset_id, asset in employee_assets.items():
            if asset.get("employee_id") == employee_id and asset.get("status") == "assigned":
                outstanding_assets.append({
                    "asset_id": asset_id,
                    "item_name": asset.get("item_name"),
                    "status": asset.get("status"),
                })

        if outstanding_assets:
            checklist_items.append({
                "task": "Collect Outstanding Assets",
                "status": "pending",
                "required": True,
                "assets": outstanding_assets,
            })

        # Check for finance settlements
        pending_settlements = []
        for settlement_id, settlement in finance_settlements.items():
            if settlement.get("employee_id") == employee_id and not settlement.get("is_cleared"):
                pending_settlements.append({
                    "settlement_id": settlement_id,
                    "amount": settlement.get("amount"),
                    "is_cleared": settlement.get("is_cleared"),
                })

        if pending_settlements:
            checklist_items.append({
                "task": "Clear Finance Settlements",
                "status": "pending",
                "required": True,
                "settlements": pending_settlements,
            })

        # Build the complete checklist response
        checklist = {
            "exit_case_id": exit_case_id,
            "employee_id": employee_id,
            "employee_name": employee.get("full_name"),
            "exit_date": exit_case.get("exit_date"),
            "reason": exit_case.get("reason"),
            "exit_clearance_status": exit_case.get("exit_clearance_status"),
            "checklist_id": offboarding_checklist_id,
            "checklist_status": offboarding_checklist.get("status"),
            "checklist_items": checklist_items,
            "total_tasks": len(checklist_items),
            "generated_at": "2025-12-12T12:00:00",
        }

        return json.dumps(checklist)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "generate_exit_checklist",
                "description": (
                    "Generates an exit checklist for an offboarding employee by retrieving "
                    "their existing offboarding checklist and associated tasks from the database. "
                    "Includes all checklist tasks, outstanding assets, and pending settlements. "
                    "Requires that initiate_offboarding has already been called for the employee."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The ID of the departing employee (required).",
                        },
                    },
                    "required": ["employee_id"],
                },
            },
        }
