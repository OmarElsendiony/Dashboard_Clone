import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class FindHouseholdUser(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        email: str,
        household_name: str,
    ) -> str:
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

        if not household_name:
            return json.dumps({"success": False, "error": "household_name is required"})

        # Convert to strings for consistent comparison
        email_str = str(email).strip()
        household_name_str = str(household_name).strip()

        # Find the household by name
        home_id = None
        home_info = None
        for hid, home in homes_dict.items():
            if not isinstance(home, dict):
                continue

            if str(home.get("home_name", "")).strip() == household_name_str:
                home_id = str(hid)
                home_info = home.copy()
                break

        if not home_id:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Household with name '{household_name_str}' not found",
                }
            )

        # Find the user by email
        user_id = None
        user_info = None
        for uid, user in users_dict.items():
            if not isinstance(user, dict):
                continue

            if str(user.get("email", "")).strip().lower() == email_str.lower():
                user_id = str(uid)
                user_info = user.copy()
                break

        if not user_id:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with email '{email_str}' not found",
                }
            )

        # Find the home_user entry linking this user to the household
        home_user_info = None
        for hu_id, home_user in home_users_dict.items():
            if not isinstance(home_user, dict):
                continue

            if (
                str(home_user.get("user_id")) == user_id
                and str(home_user.get("home_id")) == home_id
            ):
                home_user_info = home_user.copy()
                home_user_info["home_user_id"] = str(hu_id)
                break

        return json.dumps(
            {
                "success": True,
                "user": user_info,
                "household_user": home_user_info,
                "household": home_info,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "find_household_user",
                "description": (
                    "Find and retrieve household user information by email and household name. "
                    "Validates that the user exists and has 'admin' role in the specified household. "
                    "Returns user details including user_id, role, and household information. "
                    "Returns an error if the household doesn't exist, the user is not found in the specified household, "
                    "or the user does not have 'admin' role."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "The email address of the user to find.",
                        },
                        "household_name": {
                            "type": "string",
                            "description": "The name of the household to search in.",
                        },
                    },
                    "required": ["email", "household_name"],
                },
            },
        }
