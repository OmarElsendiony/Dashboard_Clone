import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class CreateFlowDefinition(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        created_by_user_email: str,
        flow_name: str,
        flow_description: str = "",
    ) -> str:
        """Create a new automation flow for a household."""
        try:
            if not isinstance(data, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Invalid payload: data must be the state dictionary.",
                    }
                )

            homes = data.get("homes")
            users = data.get("users")
            routines = data.get("routines")

            if not isinstance(homes, dict) or not isinstance(users, dict) or not isinstance(routines, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Missing homes, users, or flow collections in the dataset.",
                    }
                )

            if not isinstance(home_name, str) or not home_name.strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": "home_name is required so the household can be validated.",
                    }
                )

            if not isinstance(created_by_user_email, str) or not created_by_user_email.strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": "created_by_user_email is required to associate the flow with an acting user.",
                    }
                )

            if not isinstance(flow_name, str) or not flow_name.strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": "flow_name is required. Provide the descriptive title of the automation.",
                    }
                )

            flow_description = flow_description or ""
            if not isinstance(flow_description, str):
                return json.dumps(
                    {
                        "success": False,
                        "error": "flow_description must be a string when provided.",
                    }
                )

            timestamp = "2025-12-19T23:59:00"

            home_name_clean = home_name.strip()
            flow_name_clean = flow_name.strip()
            creator_email_clean = created_by_user_email.strip().lower()

            home_matches = [
                record
                for record in homes.values()
                if isinstance(record, dict)
                and str(record.get("home_name", "")).strip().lower()
                == home_name_clean.lower()
            ]

            if not home_matches:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Household not found.",
                    }
                )

            matched_home = home_matches[0]
            home_id_str = str(matched_home.get("home_id", "")).strip()

            user_matches = [
                record
                for record in users.values()
                if isinstance(record, dict)
                and str(record.get("email", "")).strip().lower() == creator_email_clean
            ]

            if not user_matches:
                return json.dumps(
                    {
                        "success": False,
                        "error": "User not found for the provided email.",
                    }
                )

            creator_record = user_matches[0]
            if str(creator_record.get("status", "")).strip().lower() != "active":
                return json.dumps(
                    {
                        "success": False,
                        "error": "User must be active to create a flow.",
                    }
                )

            creator_user_id = str(creator_record.get("user_id", "")).strip()

            for routine in routines.values():
                if not isinstance(routine, dict):
                    continue
                if (
                    str(routine.get("home_id", "")).strip() == home_id_str
                    and str(routine.get("routine_name", "")).strip().lower()
                    == flow_name_clean.lower()
                ):
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"A flow named '{flow_name_clean}' already exists in this household.",
                        }
                    )

            numeric_ids = []
            for key in routines.keys():
                try:
                    numeric_ids.append(int(str(key)))
                except ValueError:
                    continue
            next_id = max(numeric_ids) + 1 if numeric_ids else len(routines) + 1
            new_routine_id = str(next_id)

            new_routine = {
                "routine_id": new_routine_id,
                "home_id": home_id_str,
                "created_by_user_id": creator_user_id,
                "routine_name": flow_name_clean,
                "status": "disabled",
                "description": flow_description.strip(),
                "created_at": timestamp,
                "updated_at": timestamp,
            }
            routines[new_routine_id] = new_routine

            return json.dumps(
                {
                    "success": True,
                    "message": f"Flow '{flow_name_clean}' created for household '{matched_home.get('home_name')}'.",
                    "flow": {
                        "flow_id": new_routine["routine_id"],
                        "flow_name": new_routine["routine_name"],
                        "flow_status": new_routine["status"],
                        "flow_description": new_routine["description"],
                        "home_id": matched_home.get("home_id"),
                        "home_name": matched_home.get("home_name"),
                        "created_by_user_id": creator_user_id,
                        "created_by_user_email": creator_record.get("email"),
                        "created_at": timestamp,
                        "updated_at": timestamp,
                    },
                }
            )
        except Exception as exc:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Failed to create flow definition: {exc}",
                }
            )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_flow_definition",
                "description": (
                    "Create a new automation flow for a household."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the household where the flow will be created. Must match an existing household.",
                        },
                        "created_by_user_email": {
                            "type": "string",
                            "description": "Required email of the acting user creating the flow. User must exist and be active.",
                        },
                        "flow_name": {
                            "type": "string",
                            "description": "Required descriptive name for the automation flow. Must be unique per household.",
                        },
                        "flow_description": {
                            "type": "string",
                            "description": "Optional text describing what the flow automates. Defaults to empty string when omitted.",
                        },
                    },
                    "required": ["home_name", "created_by_user_email", "flow_name"],
                },
            },
        }
