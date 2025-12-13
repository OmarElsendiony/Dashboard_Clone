import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpdateTask(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        task_id: str,
        status: Optional[str] = None,
        name: Optional[str] = None,
        due_date: Optional[str] = None,
        assigned_manager_id: Optional[str] = None
    ) -> str:
        """
        Update an existing checklist task record.
        Only provided fields will be updated.
        """
        checklist_tasks = data.get("checklist_tasks", {})
        employees = data.get("employees", {})
        timestamp = "2025-12-12T12:00:00"
        
        # Validate required parameter
        if not task_id:
            return json.dumps({
                "success": False,
                "error": "task_id is required"
            })
        
        # Validate task exists
        if task_id not in checklist_tasks:
            return json.dumps({
                "success": False,
                "error": f"task_id '{task_id}' does not reference a valid task"
            })
        
        task = checklist_tasks[task_id]
        
        # Check if at least one field is being updated
        if all(field is None for field in [status, name, due_date, assigned_manager_id]):
            return json.dumps({
                "success": False,
                "error": "At least one field must be provided to update"
            })
        
        # Validate status if provided
        if status is not None:
            valid_statuses = ["pending", "completed"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                })
        
        # Validate assigned_manager_id if provided
        if assigned_manager_id is not None:
            if assigned_manager_id not in employees:
                return json.dumps({
                    "success": False,
                    "error": f"assigned_manager_id '{assigned_manager_id}' does not reference a valid employee"
                })
            
            manager = employees[assigned_manager_id]
            if manager.get("status") != "active":
                return json.dumps({
                    "success": False,
                    "error": f"Manager '{assigned_manager_id}' is not active (status is '{manager.get('status')}')"
                })
        
        # Validate name if provided
        if name is not None:
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
        
        # Update fields
        if status is not None:
            task["status"] = status
        if name is not None:
            task["name"] = name
        if due_date is not None:
            task["due_date"] = due_date
        if assigned_manager_id is not None:
            task["assigned_manager_id"] = assigned_manager_id
        
        # Update timestamp
        task["last_updated"] = timestamp
        
        return json.dumps({
            "success": True,
            "task": task
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update an existing checklist task record. Only provided fields will be updated. Valid values for name: IT Equipment Setup, System Access Provisioning, HR Policy Review, Benefits Enrollment Complete, Account Creation & Credentials Setup, HR Documentation & Compliance Forms, Benefits Enrollment Kickoff, Payroll Setup & Bank Verification, Orientation & Welcome Session Scheduling, Manager Introduction & Team Access Setup, Mandatory Training Assignments (Security, Compliance, Code of Conduct), Workstation/Workspace Preparation, Badge/ID Card Generation, Collect Personal Information, Complete Tax Forms (W-4, State), Verify I-9 Documents, I-9 Section 1 - Employee, I-9 Section 2 - Employer, Upload ID & Eligibility Documents, Direct Deposit Setup, Review Employee Handbook, Sign Policies, Assign Equipment, Configure Payroll Profile, Complete Benefits Enrollment, Verify Benefit Eligibility Docs, Complete Background Check, Drug Screening, Send Welcome Email, Manager Introduction, Team Introduction, Required Training Assigned, Safety Training, IT/Security Training, Email Setup, Badge/ID Activation, Workstation Setup, Set 30/60/90 Day Goals, First Week Tasks, 30-Day Check-in, 90-Day Check-in, Initiate Termination Request, Collect Resignation Letter, Manager Exit Approval, Remove System Access, Disable Email, Collect Company Equipment, Return Laptop, Return Monitor, Return Company Phone, Exit Interview, Final Timesheet Completion, Retrieve Outstanding Expenses, Terminate Benefits, Final Payroll Processing, Issue Final Payslip, Archive Employee Files, Send Exit Confirmation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "Task ID (required)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Task status: pending, completed (optional)",
                            "enum": ["pending", "completed"]
                        },
                        "name": {
                            "type": "string",
                            "description": "Task name (optional)"
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Due date (optional)"
                        },
                        "assigned_manager_id": {
                            "type": "string",
                            "description": "Assigned manager ID (optional, must be an active employee)"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        }
