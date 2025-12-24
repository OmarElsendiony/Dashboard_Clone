import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetHomeInfo(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_id: Optional[str] = None,
        home_name: Optional[str] = None,
    ) -> str:
        """
        Retrieve home information for a user.
        
        Args:
            data: Environment data containing homes, home_users, users, and addresses
            user_id: Optional user ID to filter homes by user association
            home_name: Optional home name to filter specific home
        
        Returns:
            JSON string with home information including address details
        """
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })
        
        homes = data.get("homes", {})
        home_users = data.get("home_users", {})
        users = data.get("users", {})
        addresses = data.get("addresses", {})
        
        # If user_id is provided, validate it exists
        if user_id and user_id not in users:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{user_id}' not found"
            })
        
        results = []
        
        # If user_id is provided, find homes associated with this user
        if user_id:
            user_home_ids = set()
            for home_user in home_users.values():
                if home_user.get("user_id") == user_id:
                    user_home_ids.add(home_user.get("home_id"))
            
            # Filter homes by user association
            for home_id, home_data in homes.items():
                if home_id in user_home_ids:
                    # Filter by home_name if provided
                    if home_name and home_data.get("home_name") != home_name:
                        continue
                    
                    # Get address information
                    address_id = home_data.get("address_id")
                    address_info = addresses.get(address_id, {})
                    
                    # Get user role for this home
                    user_role = None
                    for home_user in home_users.values():
                        if (home_user.get("home_id") == home_id and 
                            home_user.get("user_id") == user_id):
                            user_role = home_user.get("role")
                            break
                    
                    home_info = {
                        "home_id": home_id,
                        "home_name": home_data.get("home_name"),
                        "owner_id": home_data.get("owner_id"),
                        "guest_mode_enabled": home_data.get("guest_mode_enabled"),
                        "user_role": user_role,
                        "address": {
                            "address_id": address_id,
                            "house_number": address_info.get("house_number"),
                            "street": address_info.get("street"),
                            "city": address_info.get("city"),
                            "country": address_info.get("country")
                        },
                        "created_at": home_data.get("created_at"),
                        "updated_at": home_data.get("updated_at")
                    }
                    results.append(home_info)
        else:
            # No user_id provided, return all homes or filter by home_name
            for home_id, home_data in homes.items():
                # Filter by home_name if provided
                if home_name and home_data.get("home_name") != home_name:
                    continue
                
                # Get address information
                address_id = home_data.get("address_id")
                address_info = addresses.get(address_id, {})
                
                home_info = {
                    "home_id": home_id,
                    "home_name": home_data.get("home_name"),
                    "owner_id": home_data.get("owner_id"),
                    "guest_mode_enabled": home_data.get("guest_mode_enabled"),
                    "address": {
                        "address_id": address_id,
                        "house_number": address_info.get("house_number"),
                        "street": address_info.get("street"),
                        "city": address_info.get("city"),
                        "country": address_info.get("country")
                    },
                    "created_at": home_data.get("created_at"),
                    "updated_at": home_data.get("updated_at")
                }
                results.append(home_info)
        
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
                "name": "get_home_info",
                "description": "Retrieve home information for users in the smart home system. Returns detailed home information including address details and user associations. Can filter by user_id to get homes associated with a specific user, and by home_name to get a specific home. When user_id is provided, also returns the user's role for each home (admin, member, guest, service_integrator).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "Optional user ID to filter homes by user association. Returns all homes where this user has access."
                        },
                        "home_name": {
                            "type": "string",
                            "description": "Optional home name to filter for a specific home. Case-sensitive exact match."
                        }
                    },
                    "required": []
                }
            }
        }
