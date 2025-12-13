import json
from typing import Any, Dict, List, Optional

from tau_bench.envs.tool import Tool


class CreateChecklistTask(Tool):
    """Create a single checklist task by specifying all required fields and validations."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        checklist_id: str,
        task_name: str,
        task_due_date: str,
        status: str = "pending",
        manager_id: Optional[str] = None,
    ) -> str:
        """
        Create a checklist task with.

        - checklist_id: checklist to attach the task to.
        - task_name: must come from the standard HR checklist catalog.
        - task_due_date: required YYYY-MM-DD.
        - status: pending or completed (defaults to pending).
        - manager_id: optional assigned manager; must reference an active employee if provided.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(key) for key in table.keys()) + 1)

        def validate_date(date_str: str) -> bool:
            if not isinstance(date_str, str):
                return False
            parts = date_str.split("-")
            if len(parts) != 3:
                return False
            try:
                year, month, day = map(int, parts)
            except ValueError:
                return False
            return 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        checklists = data.get("checklists")
        checklist_tasks = data.get("checklist_tasks")
        employees = data.get("employees", {})
        if not isinstance(checklists, dict) or not isinstance(checklist_tasks, dict):
            return json.dumps({"success": False, "error": "Missing checklists or checklist_tasks store"})

        if not isinstance(checklist_id, str) or not checklist_id.strip():
            return json.dumps({"success": False, "error": "checklist_id is required"})
        checklist = checklists.get(checklist_id)
        if not checklist:
            return json.dumps({"success": False, "error": f"Checklist '{checklist_id}' not found"})

        checklist_type = str(checklist.get("checklist_type", "")).strip().lower()
        onboarding_tasks: List[str] = [
            "IT Equipment Setup",
            "System Access Provisioning",
            "HR Policy Review",
            "Benefits Enrollment Complete",
            "Account Creation & Credentials Setup",
            "HR Documentation & Compliance Forms",
            "Benefits Enrollment Kickoff",
            "Payroll Setup & Bank Verification",
            "Orientation & Welcome Session Scheduling",
            "Manager Introduction & Team Access Setup",
            "Mandatory Training Assignments (Security, Compliance, Code of Conduct)",
            "Workstation/Workspace Preparation",
            "Badge/ID Card Generation",
            "Collect Personal Information",
            "Complete Tax Forms (W-4, State)",
            "Verify I-9 Documents",
            "I-9 Section 1 - Employee",
            "I-9 Section 2 - Employer",
            "Upload ID & Eligibility Documents",
            "Direct Deposit Setup",
            "Review Employee Handbook",
            "Sign Policies",
            "Assign Equipment",
            "Configure Payroll Profile",
            "Complete Benefits Enrollment",
            "Verify Benefit Eligibility Docs",
            "Complete Background Check",
            "Drug Screening",
            "Send Welcome Email",
            "Manager Introduction",
            "Team Introduction",
            "Required Training Assigned",
            "Safety Training",
            "IT/Security Training",
            "Email Setup",
            "Badge/ID Activation",
            "Workstation Setup",
            "Set 30/60/90 Day Goals",
            "First Week Tasks",
            "30-Day Check-in",
            "90-Day Check-in",
        ]
        offboarding_tasks: List[str] = [
            "Initiate Termination Request",
            "Collect Resignation Letter",
            "Manager Exit Approval",
            "Remove System Access",
            "Disable Email",
            "Collect Company Equipment",
            "Return Laptop",
            "Return Monitor",
            "Return Company Phone",
            "Exit Interview",
            "Final Timesheet Completion",
            "Retrieve Outstanding Expenses",
            "Terminate Benefits",
            "Final Payroll Processing",
            "Issue Final Payslip",
            "Archive Employee Files",
            "Send Exit Confirmation",
        ]
        if checklist_type == "onboarding":
            task_catalog = onboarding_tasks
        elif checklist_type == "offboarding":
            task_catalog = offboarding_tasks
        else:
            return json.dumps({"success": False, "error": f"Checklist '{checklist_id}' has unsupported type '{checklist_type}'"})

        task_name = task_name.strip() if isinstance(task_name, str) else ""
        if not task_name:
            return json.dumps({"success": False, "error": "task_name is required"})

        allowed_task_names: List[str] = [
            "IT Equipment Setup",
            "System Access Provisioning",
            "HR Policy Review",
            "Benefits Enrollment Complete",
            "Account Creation & Credentials Setup",
            "HR Documentation & Compliance Forms",
            "Benefits Enrollment Kickoff",
            "Payroll Setup & Bank Verification",
            "Orientation & Welcome Session Scheduling",
            "Manager Introduction & Team Access Setup",
            "Mandatory Training Assignments (Security, Compliance, Code of Conduct)",
            "Workstation/Workspace Preparation",
            "Badge/ID Card Generation",
            "Collect Personal Information",
            "Complete Tax Forms (W-4, State)",
            "Verify I-9 Documents",
            "I-9 Section 1 - Employee",
            "I-9 Section 2 - Employer",
            "Upload ID & Eligibility Documents",
            "Direct Deposit Setup",
            "Review Employee Handbook",
            "Sign Policies",
            "Assign Equipment",
            "Configure Payroll Profile",
            "Complete Benefits Enrollment",
            "Verify Benefit Eligibility Docs",
            "Complete Background Check",
            "Drug Screening",
            "Send Welcome Email",
            "Manager Introduction",
            "Team Introduction",
            "Required Training Assigned",
            "Safety Training",
            "IT/Security Training",
            "Email Setup",
            "Badge/ID Activation",
            "Workstation Setup",
            "Set 30/60/90 Day Goals",
            "First Week Tasks",
            "30-Day Check-in",
            "90-Day Check-in",
            "Initiate Termination Request",
            "Collect Resignation Letter",
            "Manager Exit Approval",
            "Remove System Access",
            "Disable Email",
            "Collect Company Equipment",
            "Return Laptop",
            "Return Monitor",
            "Return Company Phone",
            "Exit Interview",
            "Final Timesheet Completion",
            "Retrieve Outstanding Expenses",
            "Terminate Benefits",
            "Final Payroll Processing",
            "Issue Final Payslip",
            "Archive Employee Files",
            "Send Exit Confirmation",
        ]
        allowed_lookup = {name.lower(): name for name in allowed_task_names}
        canonical_name = allowed_lookup.get(task_name.lower())
        if not canonical_name:
            return json.dumps({"success": False, "error": "task_name must match the standard checklist task catalog"})

        if not task_due_date or not validate_date(task_due_date):
            return json.dumps({"success": False, "error": "task_due_date must be YYYY-MM-DD"})

        status_value = status.strip().lower() if isinstance(status, str) else "pending"
        if status_value not in {"pending", "completed"}:
            return json.dumps({"success": False, "error": "status must be pending or completed"})

        assigned_manager = None
        if manager_id:
            if not isinstance(manager_id, str) or not manager_id.strip():
                return json.dumps({"success": False, "error": "manager_id must be a valid string"})
            manager = employees.get(manager_id)
            if not manager:
                return json.dumps({"success": False, "error": f"Manager '{manager_id}' not found"})
            mgr_status = str(manager.get("status", "")).strip().lower()
            if mgr_status != "active":
                return json.dumps({"success": False, "error": f"Manager '{manager_id}' is not active"})
            assigned_manager = manager_id

        for task in checklist_tasks.values():
            if task.get("checklist_id") == checklist_id and task.get("name", "").lower() == canonical_name.lower():
                return json.dumps({"success": False, "error": "Task already exists for this checklist"})

        timestamp = "2025-11-16T23:59:00"
        task_id = generate_id(checklist_tasks)
        record = {
            "task_id": task_id,
            "checklist_id": checklist_id,
            "name": canonical_name,
            "due_date": task_due_date,
            "assigned_manager_id": assigned_manager,
            "status": status_value,
            "created_at": timestamp,
            "last_updated": timestamp,
        }
        checklist_tasks[task_id] = record

        return json.dumps(
            {
                "success": True,
                "message": f"Task '{canonical_name}' created for checklist {checklist_id}",
                "task": record,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_checklist_task",
                "description": (
                    "Create a checklist task by providing the checklist id, task name, due date, status, "
                    "and optional manager assignment."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "checklist_id": {
                            "type": "string",
                            "description": "Checklist identifier that should receive the task.",
                        },
                        "task_name": {
                            "type": "string",
                            "description": (
                                "Name of the checklist task. Must come from the checklist catalog matching the checklist type. "
                                "Onboarding catalog: IT Equipment Setup, System Access Provisioning, HR Policy Review, Benefits Enrollment Complete, "
                                "Account Creation & Credentials Setup, HR Documentation & Compliance Forms, Benefits Enrollment Kickoff, "
                                "Payroll Setup & Bank Verification, Orientation & Welcome Session Scheduling, Manager Introduction & Team Access Setup, "
                                "Mandatory Training Assignments (Security, Compliance, Code of Conduct), Workstation/Workspace Preparation, "
                                "Badge/ID Card Generation, Collect Personal Information, Complete Tax Forms (W-4, State), Verify I-9 Documents, "
                                "I-9 Section 1 - Employee, I-9 Section 2 - Employer, Upload ID & Eligibility Documents, Direct Deposit Setup, Review Employee Handbook, "
                                "Sign Policies, Assign Equipment, Configure Payroll Profile, Complete Benefits Enrollment, Verify Benefit Eligibility Docs, "
                                "Complete Background Check, Drug Screening, Send Welcome Email, Manager Introduction, Team Introduction, Required Training Assigned, "
                                "Safety Training, IT/Security Training, Email Setup, Badge/ID Activation, Workstation Setup, Set 30/60/90 Day Goals, "
                                "First Week Tasks, 30-Day Check-in, 90-Day Check-in. "
                                "Offboarding catalog: Initiate Termination Request, Collect Resignation Letter, Manager Exit Approval, Remove System Access, "
                                "Disable Email, Collect Company Equipment, Return Laptop, Return Monitor, Return Company Phone, Exit Interview, "
                                "Final Timesheet Completion, Retrieve Outstanding Expenses, Terminate Benefits, Final Payroll Processing, Issue Final Payslip, "
                                "Archive Employee Files, Send Exit Confirmation."
                            ),
                        },
                        "task_due_date": {
                            "type": "string",
                            "description": "Due date for the task in YYYY-MM-DD format.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Task status; allowed values are pending or completed.",
                        },
                        "manager_id": {
                            "type": "string",
                            "description": "Optional manager assigned to the task; must reference an active employee when provided.",
                        },
                    },
                    "required": ["checklist_id", "task_name", "task_due_date"],
                },
            },
        }
