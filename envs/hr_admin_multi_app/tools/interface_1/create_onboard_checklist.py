import json
from typing import Any, Dict, List

from tau_bench.envs.tool import Tool


class CreateOnboardChecklist(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        task_names: List[str],
    ) -> str:
        """
        Create an onboarding checklist with specified tasks for an employee.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        employees = data.get("employees", {})
        checklists = data.setdefault("checklists", {})
        checklist_tasks = data.setdefault("checklist_tasks", {})

        # Here's a fix for interface 1
        if not isinstance(task_names, list):
            try:
                task_names = json.loads(task_names)
            except:
                return json.dumps(
                    {"success": False, "error": "task_names must be a list"}
                )

        # Validate employee exists
        if str(employee_id) not in employees:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee {employee_id} not found",
                }
            )

        # Check if checklist already exists for this employee
        for checklist_id, checklist in checklists.items():
            if (
                checklist.get("employee_id") == str(employee_id)
                and checklist.get("checklist_type") == "onboarding"
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Onboarding checklist already exists for employee {employee_id}",
                    }
                )

        if not task_names or len(task_names) == 0:
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one task must be provided for the onboarding checklist",
                }
            )

        # Validate task names against allowed enum values from schema
        valid_task_names = [
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
            "I-9 Section 1 – Employee",
            "I-9 Section 2 – Employer",
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

        for task_name in task_names:
            if task_name not in valid_task_names:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid task name '{task_name}'. Must be one of the predefined onboarding checklist tasks.",
                    }
                )

        # Generate unique checklist ID
        checklist_id = generate_id(checklists)
        current_time = "2025-11-16T23:59:00"

        # Create onboarding checklist (matches schema table 'checklists')
        checklist_data = {
            "checklist_id": checklist_id,
            "checklist_type": "onboarding",
            "employee_id": str(employee_id),
            "status": "pending",
            "created_at": current_time,
            "last_updated": current_time,
        }

        checklists[checklist_id] = checklist_data

        # Create tasks for the checklist
        created_tasks = []
        for task_name in task_names:
            task_id = f"task_{len(checklist_tasks) + 1}"
            task_data = {
                "task_id": task_id,
                "checklist_id": checklist_id,
                "name": task_name,
                "due_date": None,
                "assigned_manager_id": None,
                "status": "pending",
                "created_at": current_time,
                "last_updated": current_time,
            }
            checklist_tasks[task_id] = task_data
            created_tasks.append(task_data)

        return json.dumps(
            {
                "success": True,
                "message": f"Onboarding checklist created successfully for employee {employee_id}",
                "checklist_id": checklist_id,
                "checklist_data": checklist_data,
                "tasks": created_tasks,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_onboard_checklist",
                "description": "Creates an onboarding checklist with specified tasks for a new or existing employee. The checklist is created with a 'pending' status and contains multiple tasks that need to be completed as part of the onboarding process. Each task is created with 'pending' status, and due dates and assigned managers will be set separately using update_onboard_checklist. Used in SOP 1 (Employee Onboarding) and SOP 3 (Create Onboarding Checklist).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The unique identifier of the employee for whom the onboarding checklist is being created. Required field.",
                        },
                        "task_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of task names to include in the onboarding checklist. Each task name must be one of the predefined valid onboarding checklist task names. Required field.",
                        },
                    },
                    "required": ["employee_id", "task_names"],
                },
            },
        }
