import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class GetRisk(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        risk_id: Optional[str] = None,
        program_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for risks"
            })
        
        risks = data.get("risks", {})
        
        if not risk_id and not program_id and not status:
            return json.dumps({
                "success": False,
                "error": "At least one parameter (risk_id, program_id, or status) must be provided"
            })
            
        if status:
            valid_statuses = ["open", "closed", "escalated"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
                })
        
        if risk_id:
            if str(risk_id) not in risks:
                return json.dumps({
                    "success": False,
                    "error": f"Risk with ID '{risk_id}' not found"
                })
            
            risk = risks[str(risk_id)]
            
            if program_id and str(risk.get("project_id")) != str(program_id):
                return json.dumps({
                    "success": False,
                    "error": f"Risk does not belong to program '{program_id}'"
                })
            
            if status and str(risk.get("status")) != status:
                return json.dumps({
                    "success": False,
                    "error": f"Risk status is '{risk.get('status')}', not '{status}'"
                })
            
            risk_data = {
                "risk_id": str(risk_id),
                "program_id": str(risk.get("project_id", "")) if risk.get("project_id") is not None else None,
                "description": str(risk.get("description", "")) if risk.get("description") is not None else None,
                "work_item_id": str(risk.get("work_item_id", "")) if risk.get("work_item_id") is not None else None,
                "risk_level": str(risk.get("risk_level", "")) if risk.get("risk_level") is not None else None,
                "owner_id": str(risk.get("owner_id", "")) if risk.get("owner_id") is not None else None,
                "status": str(risk.get("status", "")) if risk.get("status") is not None else None,
                "escalated_at": str(risk.get("escalated_at", "")) if risk.get("escalated_at") is not None else None,
                "created_at": str(risk.get("created_at", "")) if risk.get("created_at") is not None else None,
                "updated_at": str(risk.get("updated_at", "")) if risk.get("updated_at") is not None else None
            }
            
            return json.dumps({
                "success": True,
                "risk_data": risk_data
            })
        
        if program_id or status:
            found_risks = []
            
            for rid, risk in risks.items():
                if program_id and str(risk.get("project_id")) != str(program_id):
                    continue
                
                if status and str(risk.get("status")) != status:
                    continue
                
                risk_data = {
                    "risk_id": str(rid),
                    "program_id": str(risk.get("project_id", "")) if risk.get("project_id") is not None else None,
                    "description": str(risk.get("description", "")) if risk.get("description") is not None else None,
                    "work_item_id": str(risk.get("work_item_id", "")) if risk.get("work_item_id") is not None else None,
                    "risk_level": str(risk.get("risk_level", "")) if risk.get("risk_level") is not None else None,
                    "owner_id": str(risk.get("owner_id", "")) if risk.get("owner_id") is not None else None,
                    "status": str(risk.get("status", "")) if risk.get("status") is not None else None,
                    "escalated_at": str(risk.get("escalated_at", "")) if risk.get("escalated_at") is not None else None,
                    "created_at": str(risk.get("created_at", "")) if risk.get("created_at") is not None else None,
                    "updated_at": str(risk.get("updated_at", "")) if risk.get("updated_at") is not None else None
                }
                
                found_risks.append(risk_data)
            
            if not found_risks:
                return json.dumps({
                    "success": False,
                    "error": "No risks found matching the specified filters"
                })
            
            if len(found_risks) == 1:
                return json.dumps({
                    "success": True,
                    "risk_data": found_risks[0]
                })
            
            return json.dumps({
                "success": True,
                "count": int(len(found_risks)),
                "risks": found_risks
            })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_risk",
                "description": "Retrieves risk information. Use this to check risk status, get risk details for reporting, identify open risks for a program, review escalated risks, or assess overall risk exposure.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "risk_id": {
                            "type": "string",
                            "description": "The unique identifier of the risk (optional if program_id or status is provided)"
                        },
                        "program_id": {
                            "type": "string",
                            "description": "Filter results by program ID (optional)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter results by status (optional). Valid values: open, closed, escalated",
                            "enum": ["open", "closed", "escalated"]
                        }
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["risk_id"]},
                        {"required": ["program_id"]},
                        {"required": ["status"]}
                    ]
                }
            }
        }
