import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreateAutomation(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        automation_name: str,
        created_by_user_email: str,
        description: Optional[str] = None,
        status: Optional[str] = "enabled",
    ) -> str:
        """
        Create a new automation.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(key) for key in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        users = data.get("users")
        routines = data.get("routines")
        home_users = data.get("home_users")

        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})
        if not isinstance(users, dict):
            return json.dumps({"success": False, "error": "users store missing"})
        if not isinstance(routines, dict):
            return json.dumps({"success": False, "error": "routines store missing"})
        if not isinstance(home_users, dict):
            return json.dumps({"success": False, "error": "home_users store missing"})

        if not isinstance(home_name, str) or not home_name.strip():
            return json.dumps({"success": False, "error": "home_name must be provided"})
        home_name = home_name.strip()

        # Find home by name
        home_id = None
        for hid, home in homes.items():
            if home.get("home_name", "").strip().lower() == home_name.lower():
                home_id = hid
                break
        
        if not home_id:
            return json.dumps({"success": False, "error": f"Home '{home_name}' not found"})

        if not isinstance(created_by_user_email, str) or not created_by_user_email.strip():
            return json.dumps({"success": False, "error": "created_by_user_email must be provided"})
        created_by_user_email = created_by_user_email.strip().lower()

        # Find user by email
        created_by_user_id = None
        created_by_user = None
        for uid, u in users.items():
            if u.get("email", "").strip().lower() == created_by_user_email:
                created_by_user_id = uid
                created_by_user = u
                break
        
        if not created_by_user_id:
            return json.dumps({"success": False, "error": f"User with email '{created_by_user_email}' not found"})

        # Ensure the user is active
        if isinstance(created_by_user, dict) and created_by_user.get("status") != "active":
            return json.dumps({"success": False, "error": f"User with email '{created_by_user_email}' is not active"})

        # SOP: created_by user must be a member/guest/admin of the specified home
        is_member = False
        for hu in home_users.values():
            if hu.get("home_id") == home_id and hu.get("user_id") == created_by_user_id:
                is_member = True
                break
        if not is_member:
            return json.dumps({
                "success": False,
                "error": f"User with email '{created_by_user_email}' does not have access to home '{home_name}'",
            })

        if not isinstance(automation_name, str) or not automation_name.strip():
            return json.dumps({"success": False, "error": "automation_name must be provided"})
        automation_name = automation_name.strip()

        for routine in routines.values():
            if routine.get("home_id") == home_id and routine.get("routine_name", "").strip().lower() == automation_name.lower():
                return json.dumps({"success": False, "error": f"Automation '{automation_name}' already exists in this home"})

        desc = description.strip() if isinstance(description, str) and description.strip() else None

        status_val = status.strip().lower() if isinstance(status, str) else "enabled"
        if status_val not in {"enabled", "disabled"}:
            return json.dumps({"success": False, "error": "status must be one of enabled, disabled"})

        routine_id = generate_id(routines)
        timestamp = "2025-12-19T23:59:00"

        record = {
            "routine_id": routine_id,
            "home_id": home_id,
            "created_by_user_id": created_by_user_id,
            "routine_name": automation_name,
            "status": status_val,
            "description": desc,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        routines[routine_id] = record

        # Return SOP terminology only (do not leak DB field names)
        presented = {
            "automation_id": record.get("routine_id"),
            "automation_name": record.get("routine_name"),
            "status": record.get("status"),
            "description": record.get("description"),
            "created_by_user_email": created_by_user_email,
            "created_at": record.get("created_at"),
            "updated_at": record.get("updated_at"),
        }
        return json.dumps({"success": True, "automation": presented})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_automation",
                "description": "Create a new automation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "automation_name": {
                            "type": "string",
                            "description": "Name of the automation; must be unique within the home.",
                        },
                        "created_by_user_email": {
                            "type": "string",
                            "description": "Email address of the user creating the automation.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional description of the automation.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Automation status; allowed values: enabled, disabled.",
                        },
                    },
                    "required": ["home_name", "automation_name", "created_by_user_email"],
                },
            },
        }

