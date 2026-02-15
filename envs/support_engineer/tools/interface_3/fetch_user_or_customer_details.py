import json
from typing import Dict, Optional, Any
from tau_bench.envs.tool import Tool


class FetchUserOrCustomerDetails(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        entity_name: str,
        email: Optional[str] = None,
        id: Optional[str] = None,
    ) -> str:
        valid_entities = ("user", "customer")

        if not entity_name:
            return json.dumps({"error": "entity_name is required"})

        if entity_name not in valid_entities:
            return json.dumps(
                {"error": f"Invalid entity_name '{entity_name}'. Must be one of: {', '.join(valid_entities)}"}
            )

        if email is None and id is None:
            return json.dumps({"error": "Either email or id must be provided"})

        def build_user_response(user):
            return {
                "user_id": str(user["user_id"]),
                "username": str(user["username"]),
                "email": str(user["email"]),
                "first_name": str(user["first_name"]),
                "last_name": str(user["last_name"]),
                "role": str(user["role"]),
                "status": str(user["status"]),
                "created_at": str(user["created_at"]),
                "updated_at": str(user["updated_at"]),
            }

        def build_customer_response(customer):
            return {
                "customer_id": str(customer["customer_id"]),
                "customer_name": str(customer["customer_name"]),
                "email": str(customer["email"]),
                "status": str(customer["status"]),
                "created_at": str(customer["created_at"]),
                "updated_at": str(customer["updated_at"]),
            }

        if entity_name == "user":
            users = data.get("users", {})
            if email is not None and id is not None:
                user = users.get(str(id))
                if not user:
                    return json.dumps(
                        {"error": f"User with ID '{id}' not found"}
                    )
                if user.get("email") != str(email):
                    return json.dumps(
                        {"error": f"Mismatch: user ID '{id}' does not correspond to email '{email}'"}
                    )
                return json.dumps({"success": True, "user": build_user_response(user)})
            if id is not None:
                user = users.get(str(id))
                if not user:
                    return json.dumps(
                        {"error": f"User with ID '{id}' not found"}
                    )
                return json.dumps({"success": True, "user": build_user_response(user)})
            user = None
            for u in users.values():
                if u.get("email") == str(email):
                    user = u
                    break
            if not user:
                return json.dumps(
                    {"error": f"User with email '{email}' not found"}
                )
            return json.dumps({"success": True, "user": build_user_response(user)})

        if entity_name == "customer":
            customers = data.get("customers", {})
            if email is not None and id is not None:
                customer = customers.get(str(id))
                if not customer:
                    return json.dumps(
                        {"error": f"Customer with ID '{id}' not found"}
                    )
                if customer.get("email") != str(email):
                    return json.dumps(
                        {"error": f"Mismatch: customer ID '{id}' does not correspond to email '{email}'"}
                    )
                return json.dumps({"success": True, "customer": build_customer_response(customer)})
            if id is not None:
                customer = customers.get(str(id))
                if not customer:
                    return json.dumps(
                        {"error": f"Customer with ID '{id}' not found"}
                    )
                return json.dumps({"success": True, "customer": build_customer_response(customer)})
            customer = None
            for c in customers.values():
                if c.get("email") == str(email):
                    customer = c
                    break
            if not customer:
                return json.dumps(
                    {"error": f"Customer with email '{email}' not found"}
                )
            return json.dumps({"success": True, "customer": build_customer_response(customer)})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_user_or_customer_details",
                "description": "Fetches the details of a user or customer. It should be used when you need to retrieve information about a specific user or customer.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entity_name": {
                            "type": "string",
                            "description": "The type of entity to fetch",
                            "enum": ["user", "customer"],
                        },
                        "email": {
                            "type": "string",
                            "description": "The email address of the user or customer",
                        },
                        "id": {
                            "type": "string",
                            "description": "The unique identifier of the user or customer. Maps to user_id when entity_name is 'user' and customer_id when entity_name is 'customer'",
                        },
                    },
                    "required": ["entity_name"],
                    "oneOf": [
                        {"required": ["email"]},
                        {"required": ["id"]},
                    ],
                },
            },
        }
