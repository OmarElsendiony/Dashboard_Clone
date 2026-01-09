import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpdateIssues(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        access_token: str,
        repository_id: str,
        title: str,
        author_id: str,
        issue_id: Optional[str] = None,
        description: Optional[str] = None,
        assignee_id: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        issue_type: Optional[str] = None
    ) -> str:
        """
        Creates or updates an issue.
        """
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        timestamp = "2026-01-01T23:59:00"

        try:
            encoded_input_token = base64.b64encode(access_token.encode('utf-8')).decode('utf-8')
        except Exception:
            return json.dumps({"error": "Failed to process access token"})

        tokens = data.get("access_tokens", {})
        valid_token = False

        for token in tokens.values():
            if token.get("token_encoded") == encoded_input_token and token.get("status") == "active":
                if token.get("expires_at") > timestamp:
                    valid_token = True
                    break
        
        if not valid_token:
            return json.dumps({"error": "Invalid or expired access token"})

        issues = data.get("issues", {})
        repositories = data.get("repositories", {})
        users = data.get("users", {})

        # Validation
        if repository_id not in repositories:
            return json.dumps({"error": f"Repository {repository_id} not found"})
        if author_id not in users:
            return json.dumps({"error": f"Author {author_id} not found"})
        if assignee_id and assignee_id not in users:
            return json.dumps({"error": f"Assignee {assignee_id} not found"})

        # Correction: Updated status to user_status enum as requested
        valid_statuses = ['active', 'suspended', 'deleted']
        if status and status not in valid_statuses:
            return json.dumps({"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"})

        # Correction: Removed 'critical'
        valid_priorities = ['low', 'medium', 'high']
        if priority and priority not in valid_priorities:
            return json.dumps({"error": f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"})

        # Correction: Updated 'documentation' to 'doc' and removed others
        valid_types = ['bug', 'feature', 'doc']
        if issue_type and issue_type not in valid_types:
            return json.dumps({"error": f"Invalid issue_type. Must be one of: {', '.join(valid_types)}"})

        # Update or Create
        if issue_id:
            if issue_id not in issues:
                return json.dumps({"error": f"Issue {issue_id} not found"})

            issue = issues[issue_id]
            # Title is required in signature, so it overwrites.
            issue["title"] = title
            
            # Only update optional fields if they are explicitly provided
            if description is not None:
                issue["description"] = description
            if assignee_id is not None:
                issue["assignee_id"] = assignee_id
            if priority is not None:
                issue["priority"] = priority
            if issue_type is not None:
                issue["issue_type"] = issue_type
            
            if status is not None:
                issue["status"] = status
                # Note: closed_at logic removed as 'closed' is no longer a valid status
                if status == 'deleted': 
                     issue["closed_at"] = timestamp # Optional: Treating deleted as closed for logic continuity

            issue["updated_at"] = timestamp
            issues[issue_id] = issue
            return json.dumps(issue)

        else:
            # Create
            new_id = generate_id(issues)

            # Correction: Explicit int conversion for issue_number calculation
            repo_issue_numbers = [int(i["issue_number"]) for i in issues.values() if i["repository_id"] == repository_id]
            next_number = max(repo_issue_numbers) + 1 if repo_issue_numbers else 1

            # Apply defaults for creation
            final_status = status if status is not None else 'active'
            final_type = issue_type if issue_type is not None else 'bug'

            new_issue = {
                "issue_id": new_id,
                "repository_id": repository_id,
                "issue_number": int(next_number), # Explicit cast
                "title": title,
                "description": description,
                "author_id": author_id,
                "assignee_id": assignee_id,
                "status": final_status,
                "priority": priority,
                "issue_type": final_type,
                "created_at": timestamp,
                "updated_at": timestamp,
                "closed_at": None
            }
            issues[new_id] = new_issue
            return json.dumps(new_issue)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_issues",
                "description": "Creates a new issue or updates an existing one.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "access_token": {
                            "type": "string",
                            "description": "The access token for authentication."
                        },
                        "issue_id": {
                            "type": "string",
                            "description": "The ID of the issue. If provided, updates existing issue; otherwise creates new."
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "The ID of the repository."
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the issue."
                        },
                        "author_id": {
                            "type": "string",
                            "description": "The user ID of the author."
                        },
                        "description": {
                            "type": "string",
                            "description": "The description of the issue."
                        },
                        "assignee_id": {
                            "type": "string",
                            "description": "The user ID of the assignee."
                        },
                        "status": {
                            "type": "string",
                            "description": "Status of the issue. Allowed values: 'active', 'suspended', 'deleted'. Default: 'active'."
                        },
                        "priority": {
                            "type": "string",
                            "description": "Priority level. Allowed values: 'low', 'medium', 'high'."
                        },
                        "issue_type": {
                            "type": "string",
                            "description": "Type of issue. Allowed values: 'bug', 'feature', 'doc'. Default: 'bug'."
                        }
                    },
                    "required": ["access_token", "repository_id", "title", "author_id"]
                }
            }
        }