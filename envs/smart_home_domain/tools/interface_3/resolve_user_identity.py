import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class ResolveUserIdentity(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_reference: Dict[str, Any],
        user_status: str = "active",
    ) -> str:
        """
        Identify a household user using user details (email, phone, first_name, last_name),
        """
        try:
            if not isinstance(data, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Smart Home dataset must be provided as a dictionary.",
                    }
                )

            if not isinstance(user_reference, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "user_reference must be an object containing the user cues.",
                    }
                )

            users_table = data.get("users")
            if not isinstance(users_table, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Users catalog is unavailable; cannot resolve household identities.",
                    }
                )

            email = user_reference.get("email")
            first_name = user_reference.get("first_name")
            last_name = user_reference.get("last_name")
            account_id = user_reference.get("user_id")

            if not any(
                [
                    isinstance(email, str) and email.strip(),
                    (
                        isinstance(first_name, str)
                        and isinstance(last_name, str)
                        and first_name.strip()
                        and last_name.strip()
                    ),
                    account_id is not None and str(account_id).strip(),
                ]
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Provide at least one identifier: email, first_name and last_name, or user_id.",
                    }
                )

            expectation = user_status.lower().strip() if isinstance(user_status, str) else ""
            if expectation not in {"active", "inactive"}:
                return json.dumps(
                    {
                        "success": False,
                        "error": "user_status must be 'active' or 'inactive'.",
                    }
                )

            email_cmp = email.lower().strip() if isinstance(email, str) else None
            first_cmp = first_name.lower().strip() if isinstance(first_name, str) else None
            last_cmp = last_name.lower().strip() if isinstance(last_name, str) else None
            account_cmp = str(account_id).strip() if account_id is not None else None

            matches = []
            for record in users_table.values():
                if not isinstance(record, dict):
                    continue

                record_email = record.get("email", "")
                record_first = record.get("first_name", "")
                record_last = record.get("last_name", "")
                record_status = record.get("status", "")
                record_id = str(record.get("user_id", "") or "")

                candidate_matches = [
                    not email_cmp or record_email.lower() == email_cmp,
                    not first_cmp or record_first.lower() == first_cmp,
                    not last_cmp or record_last.lower() == last_cmp,
                    not account_cmp or record_id == account_cmp,
                ]

                if all(candidate_matches):
                    if expectation and record_status != expectation:
                        continue
                    matches.append(record)

            if not matches:
                return json.dumps(
                    {
                        "success": False,
                        "error": "No household user matched the provided attributes. Refine the details or confirm the user status.",
                    }
                )

            response = {
                "success": True,
                "household_users": [
                    {
                        "user_id": record.get("user_id"),
                        "email": record.get("email"),
                        "first_name": record.get("first_name"),
                        "last_name": record.get("last_name"),
                        "phone_number": record.get("phone_number"),
                        "status": record.get("status"),
                        "created_at": record.get("created_at"),
                        "updated_at": record.get("updated_at"),
                    }
                    for record in matches
                ]
            }
            return json.dumps(response)
        except Exception as exc:
            return json.dumps(
                {
                    "success": False,
                    "error": f"resolve_user_identity failed: {exc}",
                }
            )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "resolve_user_identity",
                "description": (
                    "Identify a household user using contact cues (email, phone, or first_name and last_name)"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_reference": {
                            "type": "object",
                            "description": (
                                "Required. Supply at least one identifier for the household user: email, "
                                "first_name and last_name, or user_id."
                            ),
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "email": {
                                        "type": "string",
                                        "description": "Email address of the household user."
                                    },
                                    "first_name": {
                                        "type": "string",
                                        "description": "First name of the household user."
                                    },
                                    "last_name": {
                                        "type": "string",
                                        "description": "Last name of the household user."
                                    },
                                    "user_id": {
                                        "type": "string",
                                        "description": "Unique account identifier for the user."
                                    }
                                }
                            }
                        },
                        "user_status": {
                            "type": "string",
                            "description": (
                                "Optional. Defaults to 'active'. Accepts 'active' or 'inactive' to constrain the match to that status."
                            ),
                        },
                    },
                    "required": ["user_reference"],
                },
            },
        }
