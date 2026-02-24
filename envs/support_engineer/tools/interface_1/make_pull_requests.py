import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class MakePullRequests(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        source_branch: str,
        title: str,
        description: str,
        ticket_id: str,
        author_id: str,
        target_branch: Optional[str] = "main",
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not repository_id:
            return json.dumps({"success": False, "error": "Missing Argument: 'repository_id' is required."})

        if not source_branch:
            return json.dumps({"success": False, "error": "Missing Argument: 'source_branch' is required."})

        if not title:
            return json.dumps({"success": False, "error": "Missing Argument: 'title' is required."})

        if not description:
            return json.dumps({"success": False, "error": "Missing Argument: 'description' is required."})

        if not ticket_id:
            return json.dumps({"success": False, "error": "Missing Argument: 'ticket_id' is required."})

        if not author_id:
            return json.dumps({"success": False, "error": "Missing Argument: 'author_id' is required."})

        repository_id = str(repository_id).strip()
        source_branch = str(source_branch).strip()
        target_branch = str(target_branch).strip() if target_branch else "main"
        title = str(title).strip()
        description = str(description).strip()
        ticket_id = str(ticket_id).strip()
        author_id = str(author_id).strip()

        branches = data.get("branches", {})
        pull_requests = data.get("pull_requests", {})
        files_db = data.get("files", {})
        tickets = data.get("tickets", {})

        branch_id = None
        for b in branches.values():
            if isinstance(b, dict):
                if str(b.get("repository_id")) == repository_id and str(b.get("branch_name")) == source_branch:
                    branch_id = str(b.get("branch_id"))
                    break

        detected_files = []
        if branch_id:
            for f in files_db.values():
                if isinstance(f, dict):
                    if str(f.get("branch_id")) == branch_id:
                        detected_files.append(str(f.get("file_name")))

        ticket = tickets.get(ticket_id, {})
        ticket_number = ticket.get("ticket_number", ticket_id)
        gate_traceability = f"Closes {ticket_number}" in description

        gate_coverage = False
        for f in detected_files:
            fname = f.lower()
            if "test" in fname or "spec" in fname:
                gate_coverage = True
                break

        try:
            numeric_keys = [int(k) for k in pull_requests.keys() if str(k).isdigit()]
            new_id = str(max(numeric_keys) + 1) if numeric_keys else "1"
        except ValueError:
            new_id = str(len(pull_requests) + 1)

        timestamp = "2026-02-02 23:59:00"

        new_pr = {
            "pull_request_id": new_id,
            "repository_id": repository_id,
            "pull_request_number": int(new_id),
            "title": title,
            "description": description,
            "source_branch_name": source_branch,
            "target_branch_name": target_branch,
            "author_id": author_id,
            "status": "open",
            "linked_ticket_id": ticket_id,
            "gate_traceability": bool(gate_traceability),
            "gate_test_coverage": bool(gate_coverage),
            "gate_ci_status": "Pending",
            "is_emergency_fix": False,
            "assigned_team_lead": None,
            "merged_by": None,
            "merged_at": None,
            "closed_at": None,
            "created_at": timestamp,
            "updated_at": timestamp
        }

        pull_requests[new_id] = new_pr

        msg = f"Pull Request #{new_id} created with {len(detected_files)} files."
        if not gate_traceability:
            msg += f" WARNING: Traceability Gate Failed (Description missing 'Closes {ticket_number}')."
        if not gate_coverage:
            msg += " WARNING: Coverage Gate Failed (No test files detected)."

        return json.dumps({
            "success": True,
            "pull_request": new_pr,
            "message": msg
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "make_pull_requests",
                "description": (
                    " Opens a new Pull Request (PR) from a working branch into a target branch.\n"
                    " Purpose: Submits code for review and automatically runs validation gates. It checks for strict traceability by looking for 'Closes [Ticket_Number]' in the description, and verifies test coverage by scanning the files associated with the source branch.\n"
                    " When to use: Use this tool in the 'Validate and Submit Pull Requests' step after code has been committed to a branch and needs to be merged to resolve a support ticket.\n"
                    " Returns: Returns a JSON string containing a success boolean, the newly created pull request dictionary object, and a message indicating the status of the Traceability and Test Coverage gates."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository where the PR is being created."
                        },
                        "source_branch": {
                            "type": "string",
                            "description": "The name of the branch containing the code changes (e.g., 'fix/TKT-001-fix-bug')."
                        },
                        "title": {
                            "type": "string",
                            "description": "A short summary or title of the Pull Request."
                        },
                        "description": {
                            "type": "string",
                            "description": "The detailed description of the PR. MUST contain the exact text 'Closes [Ticket_Number]' (e.g. 'Closes TKT-001634') to pass the Traceability Gate."
                        },
                        "ticket_id": {
                            "type": "string",
                            "description": "The support ticket identifier that this PR resolves."
                        },
                        "author_id": {
                            "type": "string",
                            "description": "The user identifier of the person creating the pull request."
                        },
                        "target_branch": {
                            "type": "string",
                            "description": "The branch to merge into. Defaults to 'main'."
                        }
                    },
                    "required": [
                        "repository_id",
                        "source_branch",
                        "title",
                        "description",
                        "ticket_id",
                        "author_id"
                    ]
                }
            }
        }
