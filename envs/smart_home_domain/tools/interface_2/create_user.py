import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateUser(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: str,
        email: str,
        role: str,
        guest_expiration: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> str:
        """
        Create a new user and associate them with a home.
        
        Args:
            data: Environment data containing users, homes, and home_users
            home_id: Home ID to associate the user with
            email: User's email address (must be unique)
            role: User's role in the home (admin, member, guest, service_integrator)
            guest_expiration: Optional expiration datetime for guest access only (YYYY-MM-DDTHH:MM:SS)
            first_name: Optional user's first name
            last_name: Optional user's last name
            phone_number: Optional user's phone number
        
        Returns:
            JSON string with created user and home_user association data
        """
        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        def validate_email_format(email: str) -> bool:
            """Basic email format validation"""
            return "@" in email and "." in email.split("@")[1]
        
        timestamp = "2025-12-19T23:59:00"
        
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })
        
        users = data.get("users", {})
        homes = data.get("homes", {})
        home_users = data.get("home_users", {})
        
        # Validate required parameters
        if not all([home_id, email, role]):
            return json.dumps({
                "success": False,
                "error": "Missing required parameters. Required: home_id, email, role"
            })
        
        # Validate home exists
        if home_id not in homes:
            return json.dumps({
                "success": False,
                "error": f"Home with ID '{home_id}' not found"
            })
        
        # Validate email format
        if not validate_email_format(email):
            return json.dumps({
                "success": False,
                "error": "Invalid email format"
            })
        
        # Check for duplicate email
        for existing_user in users.values():
            if existing_user.get("email", "").lower() == email.lower():
                return json.dumps({
                    "success": False,
                    "error": f"User with email '{email}' already exists"
                })
        
        # Validate role
        valid_roles = ["admin", "member", "guest", "service_integrator"]
        if role not in valid_roles:
            return json.dumps({
                "success": False,
                "error": f"Invalid role '{role}'. Must be one of: {', '.join(valid_roles)}"
            })
        
        # Validate guest_expiration usage
        if guest_expiration and role != "guest":
            return json.dumps({
                "success": False,
                "error": "guest_expiration can only be set for users with role 'guest'"
            })
        
        # Validate guest_expiration format if provided
        if guest_expiration:
            try:
                # Basic validation for datetime format YYYY-MM-DDTHH:MM:SS
                if len(guest_expiration) != 19 or guest_expiration[10] != 'T':
                    return json.dumps({
                        "success": False,
                        "error": "Invalid guest_expiration format. Use YYYY-MM-DDTHH:MM:SS"
                    })
            except:
                return json.dumps({
                    "success": False,
                    "error": "Invalid guest_expiration format. Use YYYY-MM-DDTHH:MM:SS"
                })
        
        # Generate new user ID
        new_user_id = generate_id(users)
        
        # Create new user record
        new_user = {
            "user_id": new_user_id,
            "email": email.lower().strip(),
            "first_name": first_name.strip() if first_name else None,
            "last_name": last_name.strip() if last_name else None,
            "phone_number": phone_number.strip() if phone_number else None,
            "status": "active",
            "created_at": timestamp,
            "updated_at": timestamp
        }
        
        # Add user to users table
        users[new_user_id] = new_user
        
        # Generate new home_user ID
        new_home_user_id = generate_id(home_users)
        
        # Create home_user association
        new_home_user = {
            "home_user_id": new_home_user_id,
            "home_id": home_id,
            "user_id": new_user_id,
            "role": role,
            "access_expires_at": guest_expiration if role == "guest" else None,
            "created_at": timestamp,
            "updated_at": timestamp
        }
        
        # Add home_user association
        home_users[new_home_user_id] = new_home_user
        
        return json.dumps({
            "success": True,
            "message": f"User created successfully and associated with home {home_id}",
            "user": new_user,
            "home_user": new_home_user
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_user",
                "description": "Create a new user and associate them with a home in the smart home system. Creates both a user record and a home_user association record. Validates email uniqueness and format. For guest users, an expiration datetime can be set for temporary access. Role determines the user's permissions within the home.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "Home ID to associate the user with (must exist in the system)"
                        },
                        "email": {
                            "type": "string",
                            "description": "User's email address (must be unique and valid format)"
                        },
                        "role": {
                            "type": "string",
                            "description": "User's role in the home: 'admin', 'member', 'guest', 'service_integrator'",
                            "enum": ["admin", "member", "guest", "service_integrator"]
                        },
                        "guest_expiration": {
                            "type": "string",
                            "description": "Expiration datetime for guest access in format YYYY-MM-DDTHH:MM:SS (e.g., 2025-12-31T23:59:59). Only applicable when role is 'guest'. Defines when the guest's access will expire."
                        },
                        "first_name": {
                            "type": "string",
                            "description": "Optional user's first name"
                        },
                        "last_name": {
                            "type": "string",
                            "description": "Optional user's last name"
                        },
                        "phone_number": {
                            "type": "string",
                            "description": "Optional user's phone number"
                        }
                    },
                    "required": ["home_id", "email", "role"]
                }
            }
        }
