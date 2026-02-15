import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreatePullRequest(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        title: str,
        source_branch_name: str,
        target_branch_name: str,
        author_id: str,
        description: Optional[str] = None,
        linked_ticket_id: Optional[str] = None,
        assigned_team_lead: Optional[str] = None,
        status: str = "open",
        gate_ci_status: str = "Pending",
        gate_traceability: bool = False,
        gate_test_coverage: bool = False,
        is_emergency_fix: bool = False,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        def generate_id(table: Dict[str, Any]) -> str:
            return str(max([int(k) for k in table.keys()], default=0) + 1)
        pull_requests = data.setdefault("pull_requests", {})
        users = data.get("users", {})
        repositories = data.get("repositories", {})
        tickets = data.get("tickets", {})

        if not repository_id:
            return json.dumps({"success": False, "error": "Repository ID is required"})

        if not title:
            return json.dumps({"success": False, "error": "Title is required"})

        if not source_branch_name:
            return json.dumps({"success": False, "error": "Source branch name is required"})

        if not target_branch_name:
            return json.dumps({"success": False, "error": "Target branch name is required"})

        if not author_id:
            return json.dumps({"success": False, "error": "Author ID is required"})

        # Validation: Ensure Repository exists
        if repository_id not in repositories:
            return json.dumps({"success": False, "error": f"Repository ID '{repository_id}' not found"})
        # Optional Validation: Ensure linked ticket exists if provided
        if linked_ticket_id and linked_ticket_id not in tickets:
            return json.dumps({"success": False, "error": f"Linked ticket ID '{linked_ticket_id}' not found"})

        # Validation: Ensure Author exists
        if author_id not in users:
            return json.dumps({"success": False, "error": f"Author ID '{author_id}' not found"})

        # Validation: Enums
        if status.lower() not in ["open", "closed", "merged", "draft"]:
            return json.dumps({"success": False, "error": f"Invalid status: {status}"})

        if gate_ci_status.capitalize() not in ["Success", "Failure", "Pending"]:
            return json.dumps({"success": False, "error": f"Invalid CI status: {gate_ci_status}"})
        # Validate both branch names
        if not source_branch_name:
            return json.dumps({"success": False, "error": "Source branch name cannot be empty"})
        if not target_branch_name:
            return json.dumps({"success": False, "error": "Target branch name cannot be empty"})
        # ensure both branch names are not the same
        if source_branch_name == target_branch_name:
            return json.dumps({"success": False, "error": "Source and target branch names cannot be the same"})
        # Validate the branches exist in the repository
        branches = data.get("branches", {})
        source_branch_exists = any(
            branch["branch_name"] == source_branch_name and branch["repository_id"] == repository_id
            for branch in branches.values()
        )
        target_branch_exists = any(
            branch["branch_name"] == target_branch_name and branch["repository_id"] == repository_id
            for branch in branches.values()
        )
        if not source_branch_exists:
            return json.dumps({"success": False, "error": f"Source branch '{source_branch_name}' does not exist in repository '{repository_id}'"})
        if not target_branch_exists:
            return json.dumps({"success": False, "error": f"Target branch '{target_branch_name}' does not exist in repository '{repository_id}'"})
        # Validation: Assigned team lead exists if provided
        if assigned_team_lead and assigned_team_lead not in users:
            return json.dumps({"success": False, "error": f"Assigned team lead ID '{assigned_team_lead}' not found"})
        # Logic: Generate ID and Number
        new_id = generate_id(pull_requests)
        pr_number = max([pr["pull_request_number"] for pr in pull_requests.values() if pr.get('repository_id') == repository_id]) + 1

        timestamp = "2026-02-02 23:59:00"
        truthy_values = [True, 'true', 'True', 1, '1']
        # Create Object
        new_pr = {
            "pull_request_id": str(new_id),
            "repository_id": str(repository_id),
            "pull_request_number": int(pr_number),
            "title": str(title)[:500],
            "description": str(description),
            "source_branch_name": str(source_branch_name),
            "target_branch_name": str(target_branch_name),
            "author_id": str(author_id),
            "status": str(status),
            "linked_ticket_id": str(linked_ticket_id) if linked_ticket_id else None,
            "gate_traceability": gate_traceability in truthy_values,
            "gate_test_coverage": gate_test_coverage in truthy_values,
            "gate_ci_status": gate_ci_status,
            "is_emergency_fix": is_emergency_fix in truthy_values,
            "assigned_team_lead": assigned_team_lead,
            "merged_by": None,
            "merged_at": None,
            "closed_at": None,
            "created_at": timestamp,
            "updated_at": timestamp
        }

        pull_requests[new_id] = new_pr

        return json.dumps({"success": True, "pull_request": new_pr})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_pull_request",
                "description": "Initiates a new pull request (PR) to propose code changes between two existing branches within a repository. It allows for linking the PR to a specific support ticket, designating an emergency fix status, and assigning a team lead for review. Use this to manage code contributions and ensure proper review workflows are followed.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {"type": "string", "description": "The ID of the repository where the pull request is being created."},
                        "title": {"type": "string", "maxLength": 500, "description": "The title of the pull request."},
                        "source_branch_name": {"type": "string", "description": "The source branch name of the pull request."},
                        "target_branch_name": {"type": "string", "description": "The target branch name of the pull request."},
                        "author_id": {"type": "string", "description": "The ID of the author of the pull request."},
                        "description": {"type": "string", "description": "The description of the pull request."},
                        "linked_ticket_id": {"type": "string", "description": "The ID of the linked ticket, if any."},
                        "assigned_team_lead": {"type": "string", "description": "The ID of the assigned team lead."},
                        "status": {"type": "string", "enum": ["open", "closed", "merged", "draft"], "description": "The status of the pull request."},
                        "gate_ci_status": {"type": "string", "enum": ["Success", "Failure", "Pending"], "description": "The CI status of the pull request."},
                        "gate_traceability": {"type": "boolean", "description": "Whether traceability gates are satisfied."},
                        "gate_test_coverage": {"type": "boolean", "description": "Whether test coverage gates are satisfied."},
                        "is_emergency_fix": {"type": "boolean", "description": "Whether this is an emergency fix."}
                    },
                    "required": ["repository_id", "title", "source_branch_name", "target_branch_name", "author_id"]
                }
            }
        }
