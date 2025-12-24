import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class EnrollHouseholdMember(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        member_user_id: str,
        role: str,
        home_id: str = None,
        access_expires_at: str = None,
    ) -> str:
        """
        Add a user to a household (home_users table). Requires the target home (by name, optionally home_id)
        and the user to enroll. Validates that the user exists, is active, and not already in the household.
        """
        try:
            if not isinstance(data, dict):
                return json.dumps({"success": False, "error": "Smart Home dataset must be a dictionary."})

            homes = data.get("homes")
            home_users = data.get("home_users")
            users = data.get("users")
            if not isinstance(homes, dict) or not isinstance(home_users, dict) or not isinstance(users, dict):
                return json.dumps({"success": False, "error": "homes, home_users, or users table missing/invalid."})

            if not isinstance(home_name, str) or not home_name.strip():
                return json.dumps({"success": False, "error": "home_name is required."})
            if not isinstance(member_user_id, str) or not member_user_id.strip():
                return json.dumps({"success": False, "error": "member_user_id is required."})
            if not isinstance(role, str) or not role.strip():
                return json.dumps({"success": False, "error": "role is required."})
            role_norm = role.strip().lower()
            if role_norm not in {"admin", "member", "guest"}:
                return json.dumps({"success": False, "error": "role must be admin, member, or guest."})

            home_record = None
            target_home_id = None
            if isinstance(home_id, str) and home_id.strip():
                target_home_id = home_id.strip()
                home_record = homes.get(target_home_id)
            else:
                matches = [
                    (hid, record)
                    for hid, record in homes.items()
                    if isinstance(record, dict) and record.get("home_name", "").lower() == home_name.strip().lower()
                ]
                if matches:
                    target_home_id, home_record = matches[0]

            if not isinstance(home_record, dict):
                return json.dumps({"success": False, "error": "Household not found."})

            user_record = users.get(member_user_id.strip())
            if not isinstance(user_record, dict) or user_record.get("status") != "active":
                return json.dumps({"success": False, "error": "member_user_id must reference an active user."})

            already_member = any(
                isinstance(entry, dict)
                and str(entry.get("home_id")) == target_home_id
                and str(entry.get("user_id")) == member_user_id.strip()
                for entry in home_users.values()
            )
            if already_member:
                return json.dumps({"success": False, "error": "User is already enrolled in this household."})

            numeric_ids = []
            for key in home_users.keys():
                try:
                    numeric_ids.append(int(key))
                except (TypeError, ValueError):
                    continue
            new_home_user_id = str(max(numeric_ids, default=0) + 1)

            if role_norm == "guest" and not (isinstance(access_expires_at, str) and access_expires_at.strip()):
                return json.dumps({"success": False, "error": "access_expires_at is required when role is guest."})

            expires_value = access_expires_at.strip() if isinstance(access_expires_at, str) and access_expires_at.strip() else None

            record = {
                "home_user_id": new_home_user_id,
                "home_id": target_home_id,
                "user_id": member_user_id.strip(),
                "role": role_norm,
                "access_expires_at": expires_value,
                "created_at": "2025-12-19T23:59:00",
                "updated_at": "2025-12-19T23:59:00",
            }
            home_users[new_home_user_id] = record

            return json.dumps({"success": True, "home_user": record})
        except Exception as exc:
            return json.dumps({"success": False, "error": f"enroll_household_member failed: {exc}"})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "enroll_household_member",
                "description": (
                    "Enroll an active user into a household roster (home_users table). "
                    "Requires home_name, member_user_id, and role; home_id can be provided to disambiguate."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Required. Household name used to locate the home.",
                        },
                        "member_user_id": {
                            "type": "string",
                            "description": "Required. Active user identifier to enroll.",
                        },
                        "role": {
                            "type": "string",
                            "description": "Required. Member role (admin/member/guest).",
                        },
                        "home_id": {
                            "type": "string",
                            "description": "Optional. Household identifier for disambiguation.",
                        },
                        "access_expires_at": {
                            "type": "string",
                            "description": "Optional. Timestamp for access expiry (guest access).",
                        },
                    },
                    "required": ["home_name", "member_user_id", "role"],
                },
            },
        }
