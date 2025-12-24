import json
from typing import Any, Dict, List
from tau_bench.envs.tool import Tool

class GetUserHomeInfo(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        home_id: str = None,
        home_user_id: str = None,
        user_email: str = None,
        role: str = None,
    ) -> str:
        """
        Retrieve a household metadata plus the list of members that match every supplied filter.

        - home_name is required, home_id (if provided) narrows the household when duplicate names exist.
        - Member filters (home_user_id, user_email, role) are applied conjunctively: only members satisfying
          all provided member filters are returned. If no member filters are supplied, the full roster is returned.
        """
        try:
            if not isinstance(data, dict):
                return json.dumps({"success": False, "error": "Smart Home dataset must be provided as a dictionary."})

            for table_name in ("homes", "home_users", "users"):
                if not isinstance(data.get(table_name), dict):
                    return json.dumps({"success": False, "error": f"{table_name} table missing or invalid."})

            if not isinstance(home_name, str) or not home_name.strip():
                return json.dumps({"success": False, "error": "home_name is required and must be a non-empty string."})
            home_name_cmp = home_name.strip().lower()

            home_id_cmp = str(home_id).strip() if home_id is not None else None
            home_user_id_cmp = str(home_user_id).strip() if home_user_id is not None else None
            user_email_cmp = user_email.strip().lower() if isinstance(user_email, str) and user_email.strip() else None
            role_cmp = role.strip().lower() if isinstance(role, str) and role.strip() else None
            if role_cmp and role_cmp not in {"admin", "member", "guest", "service_integrator"}:
                return json.dumps({"success": False, "error": "role must be admin/member/guest/service_integrator."})

            homes = data["homes"]
            users = data["users"]
            home_users = data["home_users"]

            households = [
                home
                for home in homes.values()
                if isinstance(home, dict)
                and home.get("home_name", "").lower() == home_name_cmp
                and (not home_id_cmp or str(home.get("home_id", "")) == home_id_cmp)
            ]
            if not households:
                return json.dumps({"success": False, "error": "No household matched the provided home_name/home_id."})

            household = households[0]
            home_identifier = str(household.get("home_id"))

            def member_matches(member: Dict[str, Any]) -> bool:
                if str(member.get("home_id")) != home_identifier:
                    return False
                profile = users.get(str(member.get("user_id")))
                if user_email_cmp:
                    email = profile.get("email", "").lower() if isinstance(profile, dict) else None
                    if email != user_email_cmp:
                        return False
                if home_user_id_cmp and str(member.get("home_user_id")) != home_user_id_cmp:
                    return False
                if role_cmp and member.get("role") != role_cmp:
                    return False
                return True

            filtered_members: List[Dict[str, Any]] = []
            for home_user in home_users.values():
                if not isinstance(home_user, dict):
                    continue
                if not member_matches(home_user):
                    continue
                profile = users.get(str(home_user.get("user_id")), {})
                filtered_members.append(
                    {
                        "home_user_id": home_user.get("home_user_id"),
                        "user_id": str(home_user.get("user_id")),
                        "role": home_user.get("role"),
                        "access_expires_at": home_user.get("access_expires_at"),
                        "email": profile.get("email"),
                        "first_name": profile.get("first_name"),
                        "last_name": profile.get("last_name"),
                        "phone_number": profile.get("phone_number"),
                        "status": profile.get("status"),
                    }
                )

            if not filtered_members:
                return json.dumps({"success": False, "error": "No household members matched the given filters."})

            owner_profile = users.get(str(household.get("owner_id")), {})
            return json.dumps(
                {
                    "success": True,
                    "household": {
                        "home_id": home_identifier,
                        "household_name": household.get("home_name"),
                        "owner_user_id": str(household.get("owner_id")),
                        "owner_email": owner_profile.get("email"),
                        "guest_mode_enabled": household.get("guest_mode_enabled"),
                        "address_id": household.get("address_id"),
                        "created_at": household.get("created_at"),
                        "updated_at": household.get("updated_at"),
                    },
                    "household_members": filtered_members,
                }
            )
        except Exception as exc:
            return json.dumps({"success": False, "error": f"get_user_home_info failed: {exc}"})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_user_home_info",
                "description": (
                    "Return a household profile plus all members satisfying the provided member filters. "
                    "If no member filters are provided, every member is returned."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Required. Household name  used to locate the home.",
                        },
                        "home_id": {
                            "type": "string",
                            "description": "Optional. The ID of the home.",
                        },
                        "home_user_id": {
                            "type": "string",
                            "description": "Optional. Filters to the specific home_user entry.",
                        },
                        "user_email": {
                            "type": "string",
                            "description": "Optional. Filters the roster to members whose email matches.",
                        },
                        "role": {
                            "type": "string",
                            "description": "Optional. Filters to members with the specified role (admin/member/guest/service_integrator).",
                        },
                    },
                    "required": ["home_name"],
                },
            },
        }
