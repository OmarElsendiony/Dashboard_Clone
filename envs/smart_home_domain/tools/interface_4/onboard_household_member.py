import json
from typing import Any, Dict, Optional
from datetime import datetime
from tau_bench.envs.tool import Tool

class OnboardHouseholdMember(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        email: str,
        role: str,
        household_id: str,
        expiry_date: Optional[str] = None,
    ) -> str:
        timestamp = "2025-12-19T23:59:00"

        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        users_dict = data.get("users", {})
        if not isinstance(users_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid users container: expected dict at data['users']",
                }
            )

        homes_dict = data.get("homes", {})
        if not isinstance(homes_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid homes container: expected dict at data['homes']",
                }
            )

        home_users_dict = data.get("home_users", {})
        if not isinstance(home_users_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid home_users container: expected dict at data['home_users']",
                }
            )

        # Validate required parameters
        if not email:
            return json.dumps({"success": False, "error": "email is required"})

        if not role:
            return json.dumps({"success": False, "error": "role is required"})

        if not household_id:
            return json.dumps({"success": False, "error": "household_id is required"})

        if expiry_date and role != "guest":
            return json.dumps(
                {
                    "success": False,
                    "error": "expiry_date can only be set for role 'guest'",
                }
            )

        # Convert to strings for consistent comparison
        email_str = str(email).strip()
        household_id_str = str(household_id).strip()
        role_str = str(role).strip()
        expiry_date_str = str(expiry_date).strip() if expiry_date else None

        if expiry_date_str:
            if datetime.fromisoformat(expiry_date_str) <= datetime.fromisoformat(
                "2025-12-19T23:59:00"
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"expiry_date must be in the future. Got: {expiry_date_str}",
                    }
                )

        # Validate role
        valid_roles = ["member", "guest", "service_integrator"]
        if role_str not in valid_roles:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid role '{role_str}'. Must be one of: {', '.join(valid_roles)}",
                }
            )

        # Find user by email
        user_id_str = None
        user_info = None
        for uid, user in users_dict.items():
            if not isinstance(user, dict):
                continue

            if str(user.get("email", "")).strip().lower() == email_str.lower():
                user_id_str = str(uid)
                user_info = user.copy()
                break

        if user_id_str is None:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with email '{email_str}' not found",
                }
            )

        # Check if household exists
        if household_id_str not in homes_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Household with ID '{household_id_str}' not found",
                }
            )

        home_info = homes_dict[household_id_str]
        if not isinstance(home_info, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid household data for ID '{household_id_str}'",
                }
            )

        # Check if user is already a member of this household
        for hu_id, home_user in home_users_dict.items():
            if not isinstance(home_user, dict):
                continue

            if (
                str(home_user.get("user_id")) == user_id_str
                and str(home_user.get("home_id")) == household_id_str
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"User with email '{email_str}' is already a member of household '{household_id_str}' (household_user_id: {hu_id})",
                    }
                )

        # Validate expiry_date format if provided
        if expiry_date_str:
            try:
                datetime.strptime(expiry_date_str, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid expiry_date format. Expected YYYY-MM-DDTHH:MM:SS format. Got: {expiry_date_str}",
                    }
                )

        # Generate new home_user_id
        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        new_home_user_id = generate_id(home_users_dict)

        # Create new home_user entry
        new_home_user = {
            "home_user_id": new_home_user_id,
            "home_id": household_id_str,
            "user_id": user_id_str,
            "role": role_str,
            "access_expires_at": expiry_date_str,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        # Add to data
        home_users_dict[new_home_user_id] = new_home_user

        new_home_user_return = new_home_user.copy()
        new_home_user_return.pop("home_id")
        new_home_user_return.pop("home_user_id")
        new_home_user_return["household_id"] = household_id_str
        new_home_user_return["household_user_id"] = new_home_user_id

        return json.dumps(
            {
                "success": True,
                "household_user": new_home_user_return,
                "message": f"User '{email_str}' successfully onboarded to household '{home_info.get('home_name')}' with role '{role_str}'",
                "user_email": user_info.get("email"),
                "user_id": user_id_str,
                "household_name": home_info.get("home_name"),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "onboard_household_member",
                "description": (
                    "Onboard a new member to a household by creating a household_user entry. "
                    "Finds the user by email and validates that the user exists. "
                    "Validates that the household exists. "
                    "Validates the role is one of: member, guest, service_integrator. "
                    "Ensures the user is not already a member of the household. "
                    "Optionally sets expiry_date (in YYYY-MM-DDTHH:MM:SS format) for temporary access, typically used for guest users. "
                    "Returns the created household_user details including the generated household_user_id."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "The email address of the user to onboard.",
                        },
                        "role": {
                            "type": "string",
                            "description": "The role for the user in the household. Accepted values: 'member', 'guest', 'service_integrator'.",
                        },
                        "household_id": {
                            "type": "string",
                            "description": "The ID of the household to onboard the user to.",
                        },
                        "expiry_date": {
                            "type": "string",
                            "description": "Optional. Expiry date for temporary access in YYYY-MM-DDTHH:MM:SS format. Null means permanent access.",
                        },
                    },
                    "required": ["email", "role", "household_id"],
                },
            },
        }
