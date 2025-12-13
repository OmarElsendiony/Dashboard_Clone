import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class ModifyPayrollData(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        earning_id: str,
        status: str,
        earning_type: Optional[str] = None
    ) -> str:
        """
        Modify payroll earning record (approve or reject).
        """
        payroll_earnings = data.get("payroll_earnings", {})
        timestamp = "2025-12-12T12:00:00"
        
        # Validate required parameter
        if not earning_id:
            return json.dumps({
                "success": False,
                "error": "earning_id is required"
            })
        
        if not status:
            return json.dumps({
                "success": False,
                "error": "status is required"
            })
        
        # Validate earning exists
        if earning_id not in payroll_earnings:
            return json.dumps({
                "success": False,
                "error": f"earning_id '{earning_id}' does not reference a valid payroll earning"
            })
        
        earning = payroll_earnings[earning_id]
        
        # Validate status - should be 'approved' or 'rejected' (mapping from 'approve'/'reject')
        if status == "approve":
            status = "approved"
        elif status == "reject":
            status = "rejected"
        
        valid_statuses = ["approved", "rejected", "pending", "require_justification"]
        if status not in valid_statuses:
            return json.dumps({
                "success": False,
                "error": f"Invalid status. Must be 'approve' (maps to 'approved') or 'reject' (maps to 'rejected')"
            })
        
        # Validate earning_type if provided
        if earning_type is not None:
            valid_earning_types = ["bonus", "incentive", "allowance", "payroll input", "commission"]
            if earning_type not in valid_earning_types:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid earning_type. Must be one of: {', '.join(valid_earning_types)}"
                })
        
        # Update fields
        earning["status"] = status
        if earning_type is not None:
            earning["earning_type"] = earning_type
        
        # Update timestamp
        earning["last_updated"] = timestamp
        
        return json.dumps({
            "success": True,
            "payroll_earning": earning
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "modify_payroll_data",
                "description": "Modify payroll earning record (approve or reject). Maps 'approve' to 'approved' and 'reject' to 'rejected' status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "earning_id": {
                            "type": "string",
                            "description": "Earning ID to modify (required)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Status: 'approve' (maps to 'approved') or 'reject' (maps to 'rejected') (required)",
                            "enum": ["approve", "reject"]
                        },
                        "earning_type": {
                            "type": "string",
                            "description": "Type of earning: bonus, incentive, allowance, payroll input, commission (optional)",
                            "enum": ["bonus", "incentive", "allowance", "payroll input", "commission"]
                        }
                    },
                    "required": ["earning_id", "status"]
                }
            }
        }
