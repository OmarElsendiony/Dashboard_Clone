import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreateTask(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        checklist_id: str,
        name: str,
        due_date: str,
        assigned_manager_id: Optional[str] = None,
        status: str = "pending"
    ) -> str:
        """
        Create a new task in a checklist.
        """
        checklist_tasks = data.get("checklist_tasks", {})
        checklists = data.get("checklists", {})
        employees = data.get("employees", {})
        timestamp = "2025-11-16T23:59:00"
        
        # Validate required fields
        if not checklist_id:
            return json.dumps({
                "success": False,
                "error": "checklist_id is required"
            })
        
        if not name:
            return json.dumps({
                "success": False,
                "error": "name is required"
            })
        
        if not due_date:
            return json.dumps({
                "success": False,
                "error": "due_date is required"
            })
        
        # Validate checklist exists
        if checklist_id not in checklists:
            return json.dumps({
                "success": False,
                "error": f"checklist_id '{checklist_id}' does not reference a valid checklist"
            })
        
        # Validate assigned_manager_id if provided
        if assigned_manager_id:
            if assigned_manager_id not in employees:
                return json.dumps({
                    "success": False,
                    "error": f"assigned_manager_id '{assigned_manager_id}' does not reference a valid employee"
                })
            
            manager = employees[assigned_manager_id]
            if manager.get("status") != "active":
                return json.dumps({
                    "success": False,
                    "error": f"Manager '{assigned_manager_id}' is not active"
                })
        
        # Validate status
        valid_statuses = ["pending", "completed"]
        if status not in valid_statuses:
            return json.dumps({
                "success": False,
                "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            })
        
        # Valid task names from onboarding_checklist enum
        valid_task_names = [
            # Onboarding
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
            # Offboarding
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
            "Send Exit Confirmation"
        ]
        
        if name not in valid_task_names:
            return json.dumps({
                "success": False,
                "error": f"Invalid task name. Must be one of the valid onboarding/offboarding checklist items."
            })
        
        # Generate new task_id
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        new_task_id = generate_id(checklist_tasks)
        
        # Create new task record
        new_task = {
            "task_id": new_task_id,
            "checklist_id": checklist_id,
            "name": name,
            "due_date": due_date,
            "assigned_manager_id": assigned_manager_id,
            "status": status,
            "created_at": timestamp,
            "last_updated": timestamp
        }
        
        checklist_tasks[new_task_id] = new_task
        
        return json.dumps({
            "success": True,
            "task": new_task
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_task",
                "description": "Create a new task in a checklist. Validates checklist exists, manager exists (if provided), and task name is valid. valid task names are: IT Equipment Setup, System Access Provisioning, HR Policy Review, Benefits Enrollment Complete, Account Creation & Credentials Setup, HR Documentation & Compliance Forms, Benefits Enrollment Kickoff, Payroll Setup & Bank Verification, Orientation & Welcome Session Scheduling, Manager Introduction & Team Access Setup, Mandatory Training Assignments (Security, Compliance, Code of Conduct), Workstation/Workspace Preparation, Badge/ID Card Generation, Collect Personal Information, Complete Tax Forms (W-4, State), Verify I-9 Documents, I-9 Section 1 - Employee, I-9 Section 2 - Employer, Upload ID & Eligibility Documents, Direct Deposit Setup, Review Employee Handbook, Sign Policies, Assign Equipment, Configure Payroll Profile, Complete Benefits Enrollment, Verify Benefit Eligibility Docs, Complete Background Check, Drug Screening, Send Welcome Email, Manager Introduction, Team Introduction, Required Training Assigned, Safety Training, IT/Security Training, Email Setup, Badge/ID Activation, Workstation Setup, Set 30/60/90 Day Goals, First Week Tasks, 30-Day Check-in, 90-Day Check-in, Initiate Termination Request, Collect Resignation Letter, Manager Exit Approval, Remove System Access, Disable Email, Collect Company Equipment, Return Laptop, Return Monitor, Return Company Phone, Exit Interview, Final Timesheet Completion, Retrieve Outstanding Expenses, Terminate Benefits, Final Payroll Processing, Issue Final Payslip, Archive Employee Files, Send Exit Confirmation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "checklist_id": {
                            "type": "string",
                            "description": "Checklist ID to add the task to (required)"
                        },
                        "name": {
                            "type": "string",
                            "description": "Task name from onboarding/offboarding checklist enum (required)"
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Due date in YYYY-MM-DD format (required)"
                        },
                        "assigned_manager_id": {
                            "type": "string",
                            "description": "Manager employee ID assigned to the task (optional)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Task status: pending, completed (optional, default: 'pending')",
                            "enum": ["pending", "completed"]
                        }
                    },
                    "required": ["checklist_id", "name", "due_date"]
                }
            }
        }
