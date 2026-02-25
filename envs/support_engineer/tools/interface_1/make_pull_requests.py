import json
from typing import Any, Dict, List, Optional
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
        file_paths: Optional[List[str]] = None,
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

        if file_paths is not None and not isinstance(file_paths, list):
            return json.dumps({"success": False, "error": "Invalid Argument: 'file_paths' must be a list of strings."})

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

        target_ticket = tickets[ticket_id]
        ticket_number = str(target_ticket.get("ticket_number", ""))

        for pr in pull_requests.values():
            if isinstance(pr, dict):
                if (str(pr.get("repository_id")) == repository_id and
                    str(pr.get("source_branch_name")) == source_branch and
                    str(pr.get("status")).lower() == "open"):
                    return json.dumps({
                        "success": False,
                        "error": "Duplicate PR Detected",
                        "message": f"An open pull request for branch '{source_branch}' already exists in repository '{repository_id}'."
                    })

        branch_id = None
        for b in branches.values():
            if isinstance(b, dict):
                if str(b.get("repository_id")) == repository_id and str(b.get("branch_name")) == source_branch:
                    branch_id = str(b.get("branch_id"))
                    break

        if not branch_id:
            return json.dumps({
                "success": False,
                "error": f"Not Found Error: source_branch '{source_branch}' not found in repository '{repository_id}'."
            })

        timestamp = "2026-02-02 23:59:00"

        if file_paths:
            max_file_id = 0
            for k in files_db.keys():
                try:
                    num = int(str(k))
                    if num > max_file_id: max_file_id = num
                except ValueError:
                    continue

            for path in file_paths:
                max_file_id += 1
                new_f_id = str(max_file_id)
                files_db[new_f_id] = {
                    "file_id": new_f_id,
                    "branch_id": branch_id,
                    "repository_id": repository_id,
                    "file_name": str(path),
                    "created_at": timestamp
                }

        detected_files = []
        for f in files_db.values():
            if isinstance(f, dict):
                if str(f.get("branch_id")) == branch_id:
                    detected_files.append(str(f.get("file_name")))

        gate_traceability = f"Closes {ticket_id}" in description

        gate_coverage = False
        for fname in detected_files:
            if "test" in fname.lower() or "spec" in fname.lower():
                gate_coverage = True
                break

        try:
            numeric_keys = [int(k) for k in pull_requests.keys() if str(k).isdigit()]
            new_pr_id = str(max(numeric_keys) + 1) if numeric_keys else "1"
        except ValueError:
            new_pr_id = str(len(pull_requests) + 1)

        new_pr = {
            "pull_request_id": new_pr_id,
            "repository_id": repository_id,
            "pull_request_number": int(new_pr_id),
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

        pull_requests[new_pr_id] = new_pr

        msg = f"Pull Request #{new_pr_id} created with {len(detected_files)} files."
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
                    "Opens a new Pull Request (PR) from a working branch into a target branch and commits associated files.\n"
                    " Purpose: Submits code for review and automatically runs validation gates. It checks for strict traceability by looking for 'Closes [Ticket_Number]' in the description, and verifies test coverage by scanning the files associated with the source branch.\n"
                    " When to use: Use this tool in the 'Validate and Submit Pull Requests' step after code has been committed to a branch and needs to be merged to resolve a support ticket.\n"
                    " Returns: Returns a JSON string containing a success boolean, the newly created pull request dictionary object, and a message indicating the status of the Traceability and Test Coverage gates. Fails if the source branch does not exist."
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
                            "description": "The name of the branch containing the code changes (e.g., 'fix/TKT-001'). MUST exist in the branches table."
                        },
                        "title": {
                            "type": "string",
                            "description": "A short summary or title of the Pull Request."
                        },
                        "description": {
                            "type": "string",
                            "description": "The detailed description of the PR. MUST contain the exact text 'Closes [Ticket ID]' to pass the Traceability Gate."
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
                        },
                        "file_paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "A list of file paths to simulate committing to this branch (e.g., ['src/app.py', 'tests/test_app.py']). Include a test file to pass the Coverage Gate."
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
