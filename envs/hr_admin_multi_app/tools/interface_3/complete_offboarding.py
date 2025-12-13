import json
from typing import Any, Dict

from tau_bench.envs.tool import Tool


class CompleteOffboarding(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        force_complete: bool = False,
    ) -> str:
        """
        Complete the offboarding process for an employee.
        
        Args:
            data: The database dictionary containing all tables.
            employee_id: The ID of the employee being offboarded (required).
            force_complete: Force completion even if tasks are pending (True/False). 
                Defaults to False.
        
        Returns:
            JSON string with the completed exit case and updated employee records.
        """
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not employee_id:
            return json.dumps({"error": "Missing required parameter: employee_id is required"})

        employee_id = str(employee_id)
        exit_cases = data.get("exit_cases", {})
        checklists = data.get("checklists", {})
        checklist_tasks = data.get("checklist_tasks", {})
        employees = data.get("employees", {})
        employee_assets = data.get("employee_assets", {})
        finance_settlements = data.get("finance_settlements", {})
        contracts = data.get("contracts", {})

        # Validate employee exists
        if employee_id not in employees:
            return json.dumps({"error": f"Employee with ID '{employee_id}' not found"})

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
        
        if exit_case.get("exit_clearance_status") == "cleared":
            return json.dumps({"error": f"Exit case for employee '{employee_id}' is already completed"})

        # Find the offboarding checklist for this employee
        offboarding_checklist_id = None
        for checklist_id, checklist in checklists.items():
            if (checklist.get("employee_id") == employee_id and 
                checklist.get("checklist_type") == "offboarding"):
                offboarding_checklist_id = checklist_id
                break

        # Check for pending tasks in the offboarding checklist
        pending_tasks = []
        if offboarding_checklist_id:
            for task_id, task in checklist_tasks.items():
                if (task.get("checklist_id") == offboarding_checklist_id and 
                    task.get("status") != "completed"):
                    pending_tasks.append({
                        "task_id": task_id,
                        "task_name": task.get("name"),
                        "status": task.get("status"),
                    })

        if pending_tasks and not force_complete:
            return json.dumps({
                "error": f"Cannot complete offboarding. {len(pending_tasks)} tasks are still pending. "
                "Use force_complete=True to override.",
                "pending_tasks": pending_tasks,
            })

        # Check for unreturned assets
        unreturned_assets = []
        for asset_id, asset in employee_assets.items():
            if asset.get("employee_id") == employee_id and asset.get("status") == "assigned":
                unreturned_assets.append({
                    "asset_id": asset_id,
                    "item_name": asset.get("item_name"),
                    "status": asset.get("status"),
                })

        if unreturned_assets and not force_complete:
            return json.dumps({
                "error": f"Cannot complete offboarding. {len(unreturned_assets)} assets not returned. "
                "Use force_complete=True to override.",
                "unreturned_assets": unreturned_assets,
            })

        # Check for uncleared settlements
        uncleared_settlements = []
        for settlement_id, settlement in finance_settlements.items():
            if settlement.get("employee_id") == employee_id and not settlement.get("is_cleared"):
                uncleared_settlements.append({
                    "settlement_id": settlement_id,
                    "amount": settlement.get("amount"),
                    "is_cleared": settlement.get("is_cleared"),
                })

        if uncleared_settlements and not force_complete:
            return json.dumps({
                "error": f"Cannot complete offboarding. {len(uncleared_settlements)} settlements not cleared. "
                "Use force_complete=True to override.",
                "uncleared_settlements": uncleared_settlements,
            })

        timestamp = "2025-11-16T23:59:00"

        # Update exit case
        exit_case["exit_clearance_status"] = "cleared"
        exit_case["last_updated"] = timestamp

        # Update offboarding checklist status to completed
        if offboarding_checklist_id and offboarding_checklist_id in checklists:
            checklists[offboarding_checklist_id]["status"] = "completed"
            checklists[offboarding_checklist_id]["last_updated"] = timestamp

        # Update employee status
        if employee_id in employees:
            employee = employees[employee_id]
            employee["status"] = "inactive"
            employee["flag_pending_settlement"] = False
            employee["last_updated"] = timestamp

        # Terminate contract if exists
        for contract_id, contract in contracts.items():
            if contract.get("employee_id") == employee_id and not contract.get("is_terminated"):
                contract["is_terminated"] = True
                contract["termination_date"] = exit_case.get("exit_date")
                contract["last_updated"] = timestamp

        return json.dumps({
            "exit_case_id": exit_case_id,
            "employee_id": employee_id,
            "exit_case": exit_case,
            "employee_status": employees.get(employee_id, {}).get("status"),
            "checklist_id": offboarding_checklist_id,
            "completion_message": f"Offboarding completed for employee {employee_id}",
            "warnings": {
                "force_completed": force_complete,
                "pending_tasks_count": len(pending_tasks) if force_complete else 0,
                "unreturned_assets_count": len(unreturned_assets) if force_complete else 0,
                "uncleared_settlements_count": len(uncleared_settlements) if force_complete else 0,
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "complete_offboarding",
                "description": (
                    "Completes the offboarding process for an employee. "
                    "Automatically finds the employee's exit case and offboarding checklist. "
                    "Marks the exit case as cleared (from exit_clearance_status enum), "
                    "sets employee status to inactive (from employee_status enum), and terminates contracts. "
                    "Validates that all tasks are complete, assets returned, and settlements cleared unless forced. "
                    "Requires that initiate_offboarding has already been called for the employee."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The ID of the employee being offboarded (required).",
                        },
                        "force_complete": {
                            "type": "boolean",
                            "description": "Force completion even if tasks are pending (True/False). Defaults to False.",
                        },
                    },
                    "required": ["employee_id"],
                },
            },
        }
