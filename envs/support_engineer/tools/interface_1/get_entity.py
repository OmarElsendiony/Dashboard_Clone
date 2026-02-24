import json
import re
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class GetEntity(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        entity: str,
        search_field: Optional[str] = None,
        query: Optional[str] = None,
        limit: Optional[int] = 25,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if entity not in ["user", "customer"]:
            return json.dumps({"success": False, "error": "Invalid Argument: 'entity' must be strictly 'user' or 'customer'."})

        if search_field is not None and not isinstance(search_field, str):
            return json.dumps({"success": False, "error": "Invalid Argument: 'search_field'"})

        if query is not None and not isinstance(query, str):
            return json.dumps({"success": False, "error": "Invalid Argument: 'query'"})

        if (search_field and not query) or (not search_field and query):
            return json.dumps({"success": False, "error": "Both 'search_field' and 'query' must be provided together, or both omitted to list all."})

        if limit is not None:
            try:
                limit = int(limit)
            except (ValueError, TypeError):
                return json.dumps({"success": False, "error": "Invalid Argument: 'limit' must be an integer."})
            if limit <= 0:
                return json.dumps({"success": False, "error": "Invalid Argument: 'limit' must be positive."})
        else:
            limit = 25

        matched = []

        if entity == "user":
            db_table = data.get("users", {})
            valid_search_fields = ["user_id", "username", "email", "first_name", "last_name", "role", "technical_expertise", "status", "created_at", "updated_at"]
            regex_fields = {"username", "email", "first_name", "last_name", "role", "technical_expertise", "status"}
        else:
            db_table = data.get("customers", {})
            valid_search_fields = ["customer_id", "customer_name", "email", "status", "sla_contract_type", "created_at", "updated_at"]
            regex_fields = {"customer_name", "email", "status", "sla_contract_type"}

        if not isinstance(db_table, dict):
            return json.dumps({"success": False, "error": f"Invalid data format: '{entity}s' table missing."})

        if search_field and query:
            if search_field not in valid_search_fields:
                return json.dumps({"success": False, "error": f"Invalid search_field for entity '{entity}': {search_field}. Valid options: {valid_search_fields}"})

            try:
                pattern = re.compile(query, re.IGNORECASE) if search_field in regex_fields else None
            except re.error:
                return json.dumps({"success": False, "error": "Invalid regex pattern in query."})

            for item in db_table.values():
                if not isinstance(item, dict):
                    continue

                raw_val = item.get(search_field)
                target_value = "" if raw_val is None else str(raw_val)

                if search_field in regex_fields:
                    if pattern.search(target_value):
                        matched.append(item)
                else:
                    if target_value == str(query):
                        matched.append(item)
        else:
            for item in db_table.values():
                if isinstance(item, dict):
                    matched.append(item)

        if entity == "user":
            matched.sort(key=lambda x: (
                "" if x.get("username") is None else str(x.get("username")).lower(),
                "" if x.get("user_id") is None else str(x.get("user_id"))
            ))
        else:
            matched.sort(key=lambda x: (
                "" if x.get("customer_name") is None else str(x.get("customer_name")).lower(),
                "" if x.get("customer_id") is None else str(x.get("customer_id"))
            ))

        matched = matched[:limit]

        if entity == "user":
            formatted_results = []
            for u in matched:
                expertise_val = u.get("technical_expertise")
                formatted_results.append({
                    "user_id": "" if u.get("user_id") is None else str(u.get("user_id")),
                    "username": "" if u.get("username") is None else str(u.get("username")),
                    "email": "" if u.get("email") is None else str(u.get("email")),
                    "first_name": "" if u.get("first_name") is None else str(u.get("first_name")),
                    "last_name": "" if u.get("last_name") is None else str(u.get("last_name")),
                    "role": "" if u.get("role") is None else str(u.get("role")),
                    "technical_expertise": "" if expertise_val is None else str(expertise_val),
                    "status": "" if u.get("status") is None else str(u.get("status")),
                    "created_at": "" if u.get("created_at") is None else str(u.get("created_at")),
                    "updated_at": "" if u.get("updated_at") is None else str(u.get("updated_at"))
                })
        else:
            customer_messages = data.get("customer_messages", {})
            if not isinstance(customer_messages, dict):
                customer_messages = {}

            formatted_results = []
            for c in matched:
                cid = "" if c.get("customer_id") is None else str(c.get("customer_id"))
                c_msgs = []
                for m in customer_messages.values():
                    if isinstance(m, dict) and str(m.get("customer_id", "")) == cid:
                        c_msgs.append({
                            "message_id": "" if m.get("message_id") is None else str(m.get("message_id")),
                            "ticket_id": "" if m.get("ticket_id") is None else str(m.get("ticket_id")),
                            "message_type": "" if m.get("message_type") is None else str(m.get("message_type")),
                            "message_content": "" if m.get("message_content") is None else str(m.get("message_content")),
                            "created_at": "" if m.get("created_at") is None else str(m.get("created_at"))
                        })

                c_msgs.sort(key=lambda x: (x["created_at"], x["message_id"]))
                formatted_results.append({
                    "customer_id": cid,
                    "customer_name": "" if c.get("customer_name") is None else str(c.get("customer_name")),
                    "email": "" if c.get("email") is None else str(c.get("email")),
                    "status": "" if c.get("status") is None else str(c.get("status")),
                    "sla_contract_type": "" if c.get("sla_contract_type") is None else str(c.get("sla_contract_type")),
                    "created_at": "" if c.get("created_at") is None else str(c.get("created_at")),
                    "updated_at": "" if c.get("updated_at") is None else str(c.get("updated_at")),
                    "messages": c_msgs
                })

        return json.dumps({
            "success": True,
            "entity_type": entity,
            "results": formatted_results,
            "returned_count": len(formatted_results),
            "matched_count": len(matched),
            "message": f"{entity.capitalize()}s retrieved successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_entity",
                "description": (
                    "A merged discovery tool that retrieves either internal user records or external customer records (including their message history) by querying a specific search field."
                    " Purpose: Replaces individual get_user and get_customer tools to consolidate lookup workflows for identity, roles, SLA contracts, or communications."
                    " When to use: Use this tool to find a 'user' (for assignment/access) or 'customer' (for SLA checks/ticket replies). Provide the entity type and the search constraints."
                    " Returns: A JSON string containing a success boolean, the matching list of dictionaries under 'results', and record counts."
                    "Search behavior and Fields:"
                    " - For entity='user': Valid fields are user_id, username, email, first_name, last_name, role, technical_expertise, status, created_at, updated_at. Regex is supported (case-insensitive) for username, email, first_name, last_name, role, technical_expertise, and status."
                    " - For entity='customer': Valid fields are customer_id, customer_name, email, status, sla_contract_type, created_at, updated_at. Regex is supported (case-insensitive) for customer_name, email, status, and sla_contract_type."
                    "Exact matches are required for IDs and timestamp fields across both entities. Case-insensitive regex search is supported for non-ID fields like email, first_name, last_name, role, technical_expertise, customer_name, etc."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entity": {
                            "type": "string",
                            "enum": ["user", "customer"],
                            "description": "Required. The type of entity to search for: 'user' or 'customer'."
                        },
                        "search_field": {
                            "type": "string",
                            "enum": [
                                "user_id",
                                "username",
                                "email",
                                "first_name",
                                "last_name",
                                "role",
                                "technical_expertise",
                                "status",
                                "created_at",
                                "updated_at",
                                "customer_id",
                                "customer_name",
                                "sla_contract_type"
                            ],
                            "description": "Optional. The specific field to search within based on the entity type. Passing a customer field for a user entity (or vice versa) will result in an error. If omitted alongside query, all records are returned."
                        },
                        "query": {
                            "type": "string",
                            "description": "Optional. The value or regex pattern to search for in the specified field."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Optional. Maximum number of records to return. Default is 25."
                        }
                    },
                    "required": ["entity"]
                }
            }
        }
