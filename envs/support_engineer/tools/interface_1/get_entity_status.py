import json
import re
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class GetEntityStatus(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        entity_type: str,
        entity_id: Optional[str] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
        username: Optional[str] = None,
    ) -> str:

        users_db = data.get('users', {})
        customers_db = data.get('customers', {})

        if not entity_type:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'entity_type' is required."
            })

        def resolve_user(search_id, search_email, search_username, search_name):
            if search_id and str(search_id) in users_db:
                return str(search_id)

            s_email = search_email.lower().strip() if search_email else None

            # Setup Regex Patterns
            name_pattern = None
            if search_name:
                name_pattern = re.compile(re.escape(search_name.strip()), re.IGNORECASE)

            username_pattern = None
            if search_username:
                # FIXED: Enable partial/regex search for username
                username_pattern = re.compile(re.escape(search_username.strip()), re.IGNORECASE)

            for uid, u_data in users_db.items():
                if not isinstance(u_data, dict): continue

                curr_email = str(u_data.get('email', '')).lower().strip()
                curr_username = str(u_data.get('username', '')).strip() # Keep case for display, but regex handles ignorecase

                curr_first = str(u_data.get('first_name', '')).strip()
                curr_last = str(u_data.get('last_name', '')).strip()
                curr_full_name = f"{curr_first} {curr_last}"

                # 1. Email Exact Match (Highest Precision)
                if s_email and curr_email == s_email:
                    return str(uid)

                # 2. Username Regex Match
                if username_pattern and username_pattern.search(curr_username):
                    return str(uid)

                # 3. Name Regex Match
                if name_pattern and name_pattern.search(curr_full_name):
                    return str(uid)

            return None

        def resolve_customer(search_id, search_email, search_name):
            if search_id and str(search_id) in customers_db:
                return str(search_id)

            s_email = search_email.lower().strip() if search_email else None

            name_pattern = None
            if search_name:
                name_pattern = re.compile(re.escape(search_name.strip()), re.IGNORECASE)

            for cid, c_data in customers_db.items():
                if not isinstance(c_data, dict): continue

                curr_email = str(c_data.get('email', '')).lower().strip()
                curr_cust_name = str(c_data.get('customer_name', '')).strip()

                if s_email and curr_email == s_email:
                    return str(cid)

                if name_pattern and name_pattern.search(curr_cust_name):
                    return str(cid)
            return None

        has_filters = any([entity_id, name, email, username])

        if entity_type == 'user':
            if not has_filters:
                all_users = []
                for uid, u in users_db.items():
                    if isinstance(u, dict):
                        all_users.append({
                            "entity_id": uid,
                            "status": u.get("status"),
                            "role": u.get("role"),
                            "username": u.get("username"),
                            "email": u.get("email"),
                            "full_name": f"{u.get('first_name')} {u.get('last_name')}",
                            "technical_expertise": u.get("technical_expertise")
                        })
                return json.dumps({
                    "success": True,
                    "entity_type": "user",
                    "count": len(all_users),
                    "results": all_users
                })

            target_id = resolve_user(entity_id, email, username, name)

            if not target_id:
                return json.dumps({
                    "success": False,
                    "error": "User Resolution Failed: Could not identify a valid User from provided inputs."
                })

            target_user = users_db.get(target_id)
            return json.dumps({
                "success": True,
                "entity_type": "user",
                "entity_id": target_id,
                "status": target_user.get("status"),
                "role": target_user.get("role"),
                "username": target_user.get("username"),
                "email": target_user.get("email"),
                "full_name": f"{target_user.get('first_name')} {target_user.get('last_name')}",
                "technical_expertise": target_user.get("technical_expertise")
            })

        elif entity_type == 'customer':
            if not has_filters:
                all_customers = []
                for cid, c in customers_db.items():
                    if isinstance(c, dict):
                        all_customers.append({
                            "entity_id": cid,
                            "name": c.get("customer_name"),
                            "status": c.get("status"),
                            "sla_tier": c.get("sla_contract_type"),
                            "email": c.get("email")
                        })
                return json.dumps({
                    "success": True,
                    "entity_type": "customer",
                    "count": len(all_customers),
                    "results": all_customers
                })

            target_id = resolve_customer(entity_id, email, name)

            if not target_id:
                return json.dumps({
                    "success": False,
                    "error": "Customer Resolution Failed: Could not identify a valid Customer from provided inputs."
                })

            target_cust = customers_db.get(target_id)
            return json.dumps({
                "success": True,
                "entity_type": "customer",
                "entity_id": target_id,
                "name": target_cust.get("customer_name"),
                "status": target_cust.get("status"),
                "sla_tier": target_cust.get("sla_contract_type"),
                "email": target_cust.get("email")
            })

        else:
            return json.dumps({
                "success": False,
                "error": "Invalid entity_type. Must be 'user' or 'customer'."
            })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_entity_status",
                "description": (
                    "A unified identity validator. "
                    "PURPOSE: Checks the status of a 'user' (for role/permissions) or 'customer' (for SLA/billing). "
                    "FEATURES: "
                    "1. List All: Provide only 'entity_type' to get all records. "
                    "2. Targeted Lookup: Provide 'entity_id', 'email', 'username', or 'name' to find a specific entity. "
                    "3. Partial Search: Both 'name' and 'username' fields support case-insensitive partial matching (e.g. 'john' finds 'john.doe')."
                    "RETURNS: Status, Role/SLA, and Metadata."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entity_type": {
                            "type": "string",
                            "enum": ["user", "customer"],
                            "description": "REQUIRED. The type of entity to validate."
                        },
                        "entity_id": {
                            "type": "string",
                            "description": "CONDITIONAL. The unique ID of the User or Customer."
                        },
                        "name": {
                            "type": "string",
                            "description": "CONDITIONAL. Partial search term for Full Name (Users) or Company Name (Customers)."
                        },
                        "email": {
                            "type": "string",
                            "description": "CONDITIONAL. Exact lookup parameter for Users or Customers."
                        },
                        "username": {
                            "type": "string",
                            "description": "CONDITIONAL. Partial search term for Username (Users only)."
                        }
                    },
                    "required": ["entity_type"]
                }
            }
        }
