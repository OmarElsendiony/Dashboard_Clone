import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetUserInfo(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        email: Optional[str] = None,
        home_id: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        """
        Retrieve user information with optional filters.
        
        Args:
            data: Environment data containing users, home_users, and homes
            email: Optional email to filter by (case-insensitive)
            home_id: Optional home ID to filter users associated with a specific home
            first_name: Optional first name to filter by (case-insensitive partial match)
            last_name: Optional last name to filter by (case-insensitive partial match)
            status: Optional status to filter by (active, inactive)
        
        Returns:
            JSON string with user information including home associations
        """
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })
        
        users = data.get("users", {})
        home_users = data.get("home_users", {})
        homes = data.get("homes", {})
        
        # Validate status if provided
        if status:
            valid_statuses = ["active", "inactive"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
                })
        
        # Validate home_id if provided
        if home_id and home_id not in homes:
            return json.dumps({
                "success": False,
                "error": f"Home with ID '{home_id}' not found"
            })
        
        results = []
        
        # If home_id is provided, find users associated with this home
        if home_id:
            home_user_ids = set()
            home_user_map = {}
            for home_user in home_users.values():
                if home_user.get("home_id") == home_id:
                    user_id = home_user.get("user_id")
                    home_user_ids.add(user_id)
                    home_user_map[user_id] = home_user
            
            # Filter users by home association
            for user_id, user_data in users.items():
                if user_id not in home_user_ids:
                    continue
                
                # Apply other filters
                if email and user_data.get("email", "").lower() != email.lower():
                    continue
                
                if first_name and first_name.lower() not in user_data.get("first_name", "").lower():
                    continue
                
                if last_name and last_name.lower() not in user_data.get("last_name", "").lower():
                    continue
                
                if status and user_data.get("status") != status:
                    continue
                
                # Get home association details
                home_user_data = home_user_map.get(user_id, {})
                
                user_info = {
                    "user_id": user_id,
                    "email": user_data.get("email"),
                    "first_name": user_data.get("first_name"),
                    "last_name": user_data.get("last_name"),
                    "phone_number": user_data.get("phone_number"),
                    "status": user_data.get("status"),
                    "home_association": {
                        "home_id": home_id,
                        "role": home_user_data.get("role"),
                        "access_expires_at": home_user_data.get("access_expires_at")
                    },
                    "created_at": user_data.get("created_at"),
                    "updated_at": user_data.get("updated_at")
                }
                results.append(user_info)
        else:
            # No home_id filter, search all users
            for user_id, user_data in users.items():
                # Apply filters
                if email and user_data.get("email", "").lower() != email.lower():
                    continue
                
                if first_name and first_name.lower() not in user_data.get("first_name", "").lower():
                    continue
                
                if last_name and last_name.lower() not in user_data.get("last_name", "").lower():
                    continue
                
                if status and user_data.get("status") != status:
                    continue
                
                # Get all home associations for this user
                user_homes = []
                for home_user in home_users.values():
                    if home_user.get("user_id") == user_id:
                        user_homes.append({
                            "home_id": home_user.get("home_id"),
                            "role": home_user.get("role"),
                            "access_expires_at": home_user.get("access_expires_at")
                        })
                
                user_info = {
                    "user_id": user_id,
                    "email": user_data.get("email"),
                    "first_name": user_data.get("first_name"),
                    "last_name": user_data.get("last_name"),
                    "phone_number": user_data.get("phone_number"),
                    "status": user_data.get("status"),
                    "home_associations": user_homes,
                    "created_at": user_data.get("created_at"),
                    "updated_at": user_data.get("updated_at")
                }
                results.append(user_info)
        
        return json.dumps({
            "success": True,
            "count": len(results),
            "results": results
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_user_info",
                "description": "Retrieve user information with optional filters. Returns user details including home associations. When home_id is provided, returns only users associated with that home along with their role and access expiration. When home_id is not provided, returns all home associations for matching users. Supports filtering by email (exact match, case-insensitive), first_name (partial match, case-insensitive), last_name (partial match, case-insensitive), and status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "Optional email to filter by (exact match, case-insensitive)"
                        },
                        "home_id": {
                            "type": "string",
                            "description": "Optional home ID to filter users associated with a specific home"
                        },
                        "first_name": {
                            "type": "string",
                            "description": "Optional first name to filter by (partial match, case-insensitive)"
                        },
                        "last_name": {
                            "type": "string",
                            "description": "Optional last name to filter by (partial match, case-insensitive)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional status to filter by: 'active', 'inactive'",
                            "enum": ["active", "inactive"]
                        }
                    },
                    "required": []
                }
            }
        }
