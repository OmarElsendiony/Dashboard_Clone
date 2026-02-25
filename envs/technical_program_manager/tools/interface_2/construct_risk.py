import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class ConstructRisk(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        risk_level: str,
        description: str,
        status: str,
        project_id: str,
        work_item_id: str,
        owner_id: str,
    ) -> str:
        timestamp = "2026-02-11T23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            """Generate a new unique ID for a record."""
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        for param_name, param_value in [
            ("risk_level", risk_level),
            ("description", description),
            ("status", status),
            ("project_id", project_id),
            ("work_item_id", work_item_id),
            ("owner_id", owner_id),
        ]:
            if not param_value or not str(param_value).strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Missing required parameter: '{param_name}'",
                    }
                )

        risk_level_str = str(risk_level).strip().lower()
        description_str = str(description).strip()
        status_str = str(status).strip().lower()
        project_id_str = str(project_id).strip()
        work_item_id_str = str(work_item_id).strip()
        owner_id_str = str(owner_id).strip()

        valid_risk_levels = ["low", "medium", "high", "critical"]
        if risk_level_str not in valid_risk_levels:
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Invalid risk_level '{risk_level_str}'. "
                        f"Must be one of: {', '.join(valid_risk_levels)}"
                    ),
                }
            )

        valid_statuses = ["open"]
        if status_str not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Invalid status '{status_str}'. " f"Must be one of 'open'"
                    ),
                }
            )

        risks_dict = data.get("risks", {})
        projects_dict = data.get("projects", {})
        work_items_dict = data.get("work_items", {})
        users_dict = data.get("users", {})

        if project_id_str not in projects_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Project with ID '{project_id_str}' not found",
                }
            )

        project = projects_dict[project_id_str]
        if not isinstance(project, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Invalid project data structure for ID '{project_id_str}'"
                    ),
                }
            )

        if work_item_id_str not in work_items_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Work item with ID '{work_item_id_str}' not found",
                }
            )

        work_item = work_items_dict[work_item_id_str]
        if not isinstance(work_item, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Invalid work item data structure for ID '{work_item_id_str}'"
                    ),
                }
            )

        if str(work_item.get("project_id", "")).strip() != project_id_str:
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Work item '{work_item_id_str}' does not belong "
                        f"to project '{project_id_str}'"
                    ),
                }
            )

        if owner_id_str not in users_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Owner user with ID '{owner_id_str}' not found",
                }
            )

        owner = users_dict[owner_id_str]
        if not isinstance(owner, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Invalid user data structure for owner ID '{owner_id_str}'"
                    ),
                }
            )

        owner_status = str(owner.get("status", "")).strip().lower()
        if owner_status != "active":
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Owner user '{owner_id_str}' is not active "
                        f"(status: '{owner_status}')"
                    ),
                }
            )

        new_risk_id = generate_id(risks_dict)

        new_risk = {
            "risk_id": str(new_risk_id),
            "project_id": str(project_id_str),
            "description": str(description_str),
            "work_item_id": str(work_item_id_str),
            "risk_level": str(risk_level_str),
            "owner_id": str(owner_id_str),
            "status": str(status_str),
            "escalated_at": None,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        risks_dict[new_risk_id] = new_risk

        return json.dumps(
            {
                "success": True,
                "risk": new_risk,
                "message": (
                    f"Risk created successfully with ID '{new_risk_id}' "
                    f"at level '{risk_level_str}' for work item '{work_item_id_str}' "
                    f"in project '{project_id_str}'"
                ),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "construct_risk",
                "description": "Creates a new risk entry for a work item within a project. "
                    "Use this to formally register the risk in the system. "
                    "The risk level must be pre-calculated by the caller before invoking this tool. ",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "risk_level": {
                            "type": "string",
                            "description": "The severity level of the risk, pre-calculated by the caller ",
                            "enum": ["low", "medium", "high", "critical"],
                        },
                        "description": {
                            "type": "string",
                            "description": "A description of the risk being registered.",
                        },
                        "status": {
                            "type": "string",
                            "description": "The initial status of the risk. ",
                            "enum": ["open"],
                        },
                        "project_id": {
                            "type": "string",
                            "description": "The unique identifier of the project this risk belongs to. ",
                        },
                        "work_item_id": {
                            "type": "string",
                            "description": "The unique identifier of the task under risk. ",
                        },
                        "owner_id": {
                            "type": "string",
                            "description": "The user_id of the owner of the work item under risk. ",
                        },
                    },
                    "required": [
                        "risk_level",
                        "description",
                        "status",
                        "project_id",
                        "work_item_id",
                        "owner_id",
                    ],
                },
            },
        }
