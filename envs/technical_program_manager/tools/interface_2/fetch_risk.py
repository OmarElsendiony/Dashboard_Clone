import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class FetchRisk(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        project_id: str,
        work_item_id: Optional[str] = None,
        risk_level: Optional[str] = None,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format. Expected 'data' to be a dictionary."
            })

        if not project_id or not isinstance(project_id, str):
            return json.dumps({
                "success": False,
                "error": "project_id missing. project_id must be provided."
            })

        projects_dict = data.get("projects", {})
        risks_dict = data.get("risks", {})

        if not isinstance(projects_dict, dict):
            return json.dumps({
                "success": False,
                "error": "The projects data structure is invalid."
            })

        if not isinstance(risks_dict, dict):
            return json.dumps({
                "success": False,
                "error": "The risks data structure is invalid."
            })

        if project_id not in projects_dict:
            return json.dumps({
                "success": False,
                "error": "No project found for the provided project_id."
            })

        filtered_risks = []

        for risk in risks_dict.values():

            if str(risk.get("project_id")) != project_id:
                continue

            if work_item_id is not None:
                if str(risk.get("work_item_id")) != str(work_item_id):
                    continue

            if risk_level is not None:
                if str(risk.get("risk_level", "")).lower() != risk_level.lower():
                    continue

            filtered_risks.append(risk)

        return json.dumps({
            "success": True,
            "project_id": str(project_id),
            "count": int(len(filtered_risks)),
            "risks": filtered_risks,
            "message": "Risk records retrieved successfully."
        })


    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_risk",
                "description": "Retrieve risk records associated with a project or a specific work item. "
                                "This function retrieves the severity and the number of risks in the project."
                                "Use this for escalation of the risks during workflows and closure readiness verification. "
                                "It also allows the system to review existing risks linked to a project or task, "
                                "so that teams can determine whether risks require escalation or confirm that, all risks have been addressed prior to project closure.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The unique identifier that represents the project whose associated risks need to be retrieved."
                        },
                        "work_item_id": {
                            "type": "string",
                            "description": "The identifier of a specific task or work item within the project."
                        },
                        "risk_level": {
                            "type": "string",
                            "enum": ["critical", "high", "medium", "low"],
                            "description": "The severity category assigned to the risk, indicating its level of impact and likelihood within the project."
                        }
                    },
                    "required": ["project_id"]
                }
            }
        }

