import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ListLabels(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        access_token: str,
        repository_id: str,
        issue_id: Optional[str] = None,
        pull_request_id: Optional[str] = None
    ) -> str:
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
            return json.dumps({"success": False, "error": "Invalid data format"})

        repositories = data.get("repositories", {})
        labels = data.get("labels", {})
        access_tokens = data.get("access_tokens", {})
        repository_collaborators = data.get("repository_collaborators", {})
        organization_members = data.get("organization_members", {})
        issues = data.get("issues", {})
        pull_requests = data.get("pull_requests", {})

        # Validate access token
        requesting_user_id = get_user_from_token(access_token, access_tokens)
        if not requesting_user_id:
            return json.dumps({"success": False, "error": "Invalid or expired access token"})

        # Check if repository exists
        if repository_id not in repositories:
            return json.dumps({"success": False, "error": f"Repository with ID '{repository_id}' not found"})

        repository = repositories[repository_id]

        # permission check
        has_access = False
        if repository.get("visibility") == "public":
            has_access = True

        if not has_access and repository.get("owner_type") == "user" and repository.get("owner_id") == requesting_user_id:
            has_access = True

        if not has_access:
            for collab in repository_collaborators.values():
                if (collab.get("repository_id") == repository_id and
                    collab.get("user_id") == requesting_user_id and
                    collab.get("status") == "active"):
                    has_access = True
                    break

        if not has_access and repository.get("owner_type") == "organization":
            for membership in organization_members.values():
                if (membership.get("organization_id") == repository.get("owner_id") and
                    membership.get("user_id") == requesting_user_id and
                    membership.get("status") == "active"):
                    has_access = True
                    break

        if not has_access:
            return json.dumps({"success": False, "error": "Insufficient permissions. You do not have access to this repository."})

        # Filter by Repository
        repo_labels = [l for l in labels.values() if l.get("repository_id") == repository_id]

        # Filter by Issue if provided
        if issue_id:
            if issue_id not in issues:
                 return json.dumps({"success": False, "error": f"Issue '{issue_id}' not found"})

            # Convert target number to string for safe comparison
            target_issue_num = str(issues[issue_id].get("issue_number"))

            filtered_labels = []
            for label in repo_labels:
                issue_ids_str = label.get("issue_ids")
                if issue_ids_str:
                    try:
                        # Parse the JSON string
                        attached_issues = json.loads(issue_ids_str)
                        if isinstance(attached_issues, list):
                            # Convert all elements in the list to strings to handle mixed types (int vs string)
                            attached_issues_str = [str(x) for x in attached_issues]
                            if target_issue_num in attached_issues_str:
                                filtered_labels.append(label)
                    except:
                        pass 
            repo_labels = filtered_labels

        # Filter by Pull Request if provided
        elif pull_request_id:
            if pull_request_id not in pull_requests:
                 return json.dumps({"success": False, "error": f"Pull Request '{pull_request_id}' not found"})

            # Convert target number to string for safe comparison
            target_pr_num = str(pull_requests[pull_request_id].get("pull_request_number"))

            filtered_labels = []
            for label in repo_labels:
                pr_ids_str = label.get("pr_ids")
                if pr_ids_str:
                    try:
                        attached_prs = json.loads(pr_ids_str)
                        if isinstance(attached_prs, list):
                            # Convert all elements in the list to strings
                            attached_prs_str = [str(x) for x in attached_prs]
                            if target_pr_num in attached_prs_str:
                                filtered_labels.append(label)
                    except:
                        pass
            repo_labels = filtered_labels

        # Sort by creation date
        repo_labels.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return json.dumps({
            "success": True,
            "repository_id": repository_id,
            "issue_id": issue_id,
            "pull_request_id": pull_request_id,
            "total_count": len(repo_labels),
            "labels": repo_labels
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_labels",
                "description": "Lists labels defined in a repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "access_token": {
                            "type": "string",
                            "description": "Access token for authentication (required)"
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Repository ID to list labels for (required)"
                        },
                        "issue_id": {
                            "type": "string",
                            "description": "Filter labels attached to this Issue ID (optional)"
                        },
                        "pull_request_id": {
                            "type": "string",
                            "description": "Filter labels attached to this Pull Request ID (optional)"
                        }
                    },
                    "required": ["access_token", "repository_id"]
                }
            }
        }
