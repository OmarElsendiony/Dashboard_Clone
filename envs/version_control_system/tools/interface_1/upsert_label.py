import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpsertLabel(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        access_token: str,
        action: str,
        repository_id: Optional[str] = None,
        label_id: Optional[str] = None,
        label_name: Optional[str] = None,
        color: Optional[str] = None,
        description: Optional[str] = None,
        pr_ids: Optional[str] = None,
        issue_ids: Optional[str] = None
    ) -> str:
        """
        Create or update a label in a repository.
        - action="create": Requires repository_id, label_name, color.
        - action="update": Requires label_id. Other fields are optional.
        """
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        def get_user_from_token(token: str, tokens_data: Dict[str, Any]) -> Optional[str]:
            """Encode token and find associated user_id"""
            try:
                encoded_token = base64.b64encode(token.encode('utf-8')).decode('utf-8')
                for token_info in tokens_data.values():
                    if token_info.get("token_encoded") == encoded_token:
                        return token_info.get("user_id")
                return None
            except:
                return None
        
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })
        
        # Validate action
        if action not in ["create", "update"]:
            return json.dumps({
                "success": False,
                "error": f"Invalid action '{action}'. Must be 'create' or 'update'"
            })
        
        repositories = data.get("repositories", {})
        labels = data.get("labels", {})
        access_tokens = data.get("access_tokens", {})
        repository_collaborators = data.get("repository_collaborators", {})
        organization_members = data.get("organization_members", {})
        
        # Validate access token
        requesting_user_id = get_user_from_token(access_token, access_tokens)
        if not requesting_user_id:
            return json.dumps({
                "success": False,
                "error": "Invalid or expired access token"
            })
        
        # Validate color format (only if provided)
        if color and (not color.startswith('#') or len(color) != 7):
            return json.dumps({
                "success": False,
                "error": f"Invalid color format '{color}'. Must be hexadecimal format like #445566"
            })

        timestamp = "2026-01-01T23:59:00"

        # --- HELPER: CHECK PERMISSIONS ---
        def check_permissions(repo_id: str, user_id: str) -> bool:
            if repo_id not in repositories:
                return False
            
            repo = repositories[repo_id]
            owner_id = repo.get("owner_id")
            owner_type = repo.get("owner_type")
            
            # 1. Owner
            if owner_type == "user" and owner_id == user_id:
                return True
            
            # 2. Collaborator (Write or Admin)
            for collab in repository_collaborators.values():
                if (collab.get("repository_id") == repo_id and
                    collab.get("user_id") == user_id and
                    collab.get("permission_level") in ["write", "admin"] and
                    collab.get("status") == "active"):
                    return True
            
            # 3. Organization Member
            if owner_type == "organization":
                for membership in organization_members.values():
                    if (membership.get("organization_id") == owner_id and
                        membership.get("user_id") == user_id and
                        membership.get("status") == "active"):
                        return True
            
            return False

        # --- UPDATE LOGIC ---
        if action == "update":
            if not label_id:
                return json.dumps({"success": False, "error": "label_id is required for update action"})
            
            if label_id not in labels:
                return json.dumps({"success": False, "error": f"Label with ID '{label_id}' not found"})
            
            label = labels[label_id]
            current_repo_id = label.get("repository_id")
            
            # Check Permissions
            if not check_permissions(current_repo_id, requesting_user_id):
                 return json.dumps({
                    "success": False,
                    "error": "Insufficient permissions. You must have write access to this repository to manage labels."
                })
            
            # Partial Updates: Only update fields that are provided
            if label_name: 
                label["label_name"] = label_name
            if color: 
                label["color"] = color
            if description is not None: 
                label["description"] = description
            if pr_ids is not None: 
                label["pr_ids"] = pr_ids
            if issue_ids is not None: 
                label["issue_ids"] = issue_ids
            
            return json.dumps({
                "success": True,
                "action": "update",
                "label_id": label_id,
                "label_data": label
            })

        # --- CREATE LOGIC ---
        elif action == "create":
            # Strict validation for Create
            if not repository_id:
                return json.dumps({"success": False, "error": "repository_id is required for create action"})
            if not label_name:
                return json.dumps({"success": False, "error": "label_name is required for create action"})
            if not color:
                return json.dumps({"success": False, "error": "color is required for create action"})
            
            if repository_id not in repositories:
                return json.dumps({"success": False, "error": f"Repository with ID '{repository_id}' not found"})

            # Check Permissions
            if not check_permissions(repository_id, requesting_user_id):
                 return json.dumps({
                    "success": False,
                    "error": "Insufficient permissions. You must have write access to this repository to create labels."
                })

            new_label_id = generate_id(labels)
            new_label = {
                "label_id": new_label_id,
                "repository_id": repository_id,
                "label_name": label_name,
                "color": color,
                "pr_ids": pr_ids,
                "issue_ids": issue_ids,
                "description": description,
                "created_at": timestamp
            }
            labels[new_label_id] = new_label
            
            return json.dumps({
                "success": True,
                "action": "create",
                "label_id": new_label_id,
                "label_data": new_label
            })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "upsert_label",
                "description": "Create or update a label in a repository. Use action='create' to make a new label (requires repository_id, name, color). Use action='update' to edit existing label (requires label_id).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Action to perform. Allowed values: 'create', 'update' (required)"
                        },
                        "access_token": {
                            "type": "string",
                            "description": "Access token for authentication (required)"
                        },
                        "label_name": {
                            "type": "string",
                            "description": "Label name (required for create, optional for update)"
                        },
                        "color": {
                            "type": "string",
                            "description": "Label color in hexadecimal format (e.g., #445566) (required for create, optional for update)"
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Repository ID (required for 'create')"
                        },
                        "label_id": {
                            "type": "string",
                            "description": "Label ID (required for 'update')"
                        },
                        "description": {
                            "type": "string",
                            "description": "Label description (optional)"
                        },
                        "pr_ids": {
                            "type": "string",
                            "description": "JSON string array of pull request IDs (e.g., '[\"1\",\"2\"]') (optional)"
                        },
                        "issue_ids": {
                            "type": "string",
                            "description": "JSON string array of issue IDs (e.g., '[\"6\",\"7\"]') (optional)"
                        }
                    },
                    "required": ["action", "access_token"]
                }
            }
        }
