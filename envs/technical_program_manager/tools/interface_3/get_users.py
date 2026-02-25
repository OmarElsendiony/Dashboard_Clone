import json
import re
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class GetUsers(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        identifier: Optional[str] = None,
        expand: Optional[str] = None,
        query: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": bool(False), "error": str("System Error: Invalid data context format.")})

        if identifier is not None:
            if not isinstance(identifier, str):
                return json.dumps({"success": bool(False), "error": str("Input Error: 'identifier' must be a string.")})
            valid_identifiers = ["user_id", "username", "email", "first_name", "last_name", "role", "status"]
            if str(identifier) not in valid_identifiers:
                return json.dumps({
                    "success": bool(False), 
                    "error": str(f"Input Error: Invalid identifier '{identifier}'. Allowed values are: {', '.join(valid_identifiers)}")
                })

        if expand is not None:
            if not isinstance(expand, str):
                return json.dumps({"success": bool(False), "error": str("Input Error: 'expand' must be a string.")})
            valid_expands = ["contact", "role", "contact, role", "role, contact"]
            if str(expand) not in valid_expands:
                return json.dumps({
                    "success": bool(False), 
                    "error": str(f"Input Error: Invalid expand '{expand}'. Allowed values are: {', '.join(valid_expands)}")
                })

        if query is not None:
            if not isinstance(query, str):
                return json.dumps({"success": bool(False), "error": str("Input Error: 'query' must be a string.")})
            
            if identifier is not None:
                if str(identifier) == "role":
                    valid_roles = ["technical_program_manager", "stakeholder", "collaborator"]
                    if str(query) not in valid_roles:
                        return json.dumps({
                            "success": bool(False),
                            "error": str(f"Input Error: Invalid query '{query}' for identifier 'role'. Allowed values are: {', '.join(valid_roles)}")
                        })
                elif str(identifier) == "status":
                    valid_statuses = ["active", "inactive"]
                    if str(query) not in valid_statuses:
                        return json.dumps({
                            "success": bool(False),
                            "error": str(f"Input Error: Invalid query '{query}' for identifier 'status'. Allowed values are: {', '.join(valid_statuses)}")
                        })

        users = data.get("users", {})
        matched_users = []

        for uid, user in users.items():
            match_query = bool(True)

            if query:
                q_str = str(query)
                q_lower = q_str.lower()
                
                if identifier:
                    field_val = str(user.get(identifier, ""))
                    if str(identifier) == "user_id":
                        if str(field_val) != str(q_str):
                            match_query = bool(False)
                    else:
                        if q_lower not in field_val.lower():
                            try:
                                if not re.search(q_str, field_val, re.IGNORECASE):
                                    match_query = bool(False)
                            except re.error:
                                match_query = bool(False)
                else:
                    u_name = str(user.get("username", ""))
                    u_email = str(user.get("email", ""))
                    f_name = str(user.get("first_name", ""))
                    l_name = str(user.get("last_name", ""))
                    
                    if (q_lower not in u_name.lower() and 
                        q_lower not in u_email.lower() and 
                        q_lower not in f_name.lower() and 
                        q_lower not in l_name.lower()):
                        try:
                            if not (re.search(q_str, u_name, re.IGNORECASE) or 
                                    re.search(q_str, u_email, re.IGNORECASE) or 
                                    re.search(q_str, f_name, re.IGNORECASE) or 
                                    re.search(q_str, l_name, re.IGNORECASE)):
                                match_query = bool(False)
                        except re.error:
                            match_query = bool(False)

            if match_query:
                user_record = {
                    "user_id": str(uid),
                    "username": str(user.get("username", "")),
                    "email": str(user.get("email", "")),
                    "first_name": str(user.get("first_name", "")),
                    "last_name": str(user.get("last_name", "")),
                    "role": str(user.get("role", "")),
                    "status": str(user.get("status", "")),
                    "created_at": str(user.get("created_at", "")),
                    "updated_at": str(user.get("updated_at", ""))
                }

                if expand:
                    exp_lower = str(expand).lower()
                    if "contact" in exp_lower:
                        user_record["contact_methodologies"] = [{"type": "email", "value": str(user.get("email", ""))}]
                    if "role" in exp_lower:
                        user_record["role_assignments"] = [str(user.get("role", ""))]

                matched_users.append(user_record)

        return json.dumps({
            "success": bool(True),
            "data": matched_users
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_users",
                "description": (
                    "Purpose: Lists account users with expansive sorting logic or retrieves specific user profile information including contact methodologies and role assignments. "
                    "When to Use: When you need to resolve a user ID, find on-call personnel, or check a team member's role and contact info. "
                    "Returns: A JSON object containing a list of matched user profiles."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "identifier": {
                            "type": "string",
                            "description": "The specific field or column to search against.",
                            "enum": ["user_id", "username", "email", "first_name", "last_name", "role", "status"]
                        },
                        "expand": {
                            "type": "string",
                            "description": "Properties to expand for contact methodologies and role assignments.",
                            "enum": ["contact", "role", "contact, role", "role, contact"]
                        },
                        "query": {
                            "type": "string",
                            "description": "The actual value to search for within the specified identifier field (or globally across names/emails if identifier is omitted). Supports partial and regex matching (except for user_id, which strictly requires an exact match). If querying against role or status, it must be a valid schema enum."
                        }
                    },
                    "required": []
                }
            }
        }
