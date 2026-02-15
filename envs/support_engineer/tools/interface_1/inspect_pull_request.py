import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class InspectPullRequest(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        pull_request_id: str,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        pull_requests = data.get("pull_requests", {})
        branches = data.get("branches", {})
        files = data.get("files", {})

        if not pull_request_id:
            return json.dumps({"success": False, "error": "Missing Argument: 'pull_request_id' is required."})

        target_pr = None
        if str(pull_request_id) in pull_requests:
            target_pr = pull_requests[str(pull_request_id)]
        else:
            return json.dumps({"success": False, "error": f"Not Found Error: Pull Request ID '{pull_request_id}' not found."})

        repo_id = target_pr.get("repository_id")
        source_branch_name = target_pr.get("source_branch_name")

        target_branch_id = None
        for b in branches.values():
            if b.get("repository_id") == repo_id and b.get("branch_name") == source_branch_name:
                target_branch_id = b.get("branch_id")
                break

        pr_files = []
        if target_branch_id:
            for f in files.values():
                if f.get("branch_id") == str(target_branch_id):

                    pr_files.append(f.get("file_path", f.get("file_name", "unknown")))

        has_tests = any("test" in f.lower() or "spec" in f.lower() for f in pr_files)

        target_pr["derived_file_list"] = pr_files
        target_pr["derived_has_tests"] = has_tests

        return json.dumps({
            "success": True,
            "pull_request": target_pr
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "inspect_pull_request",
                "description": (
                    "Retrieves detailed metadata for a specific Pull Request, including the list of changed files and validation gate status. "
                    "PURPOSE: Acts as the primary 'Read' tool for the Engineering Validation workflow. It allows the Support Engineer to audit a PR before merging. "
                    "WHEN TO USE: 1) Verifying that the 'Coverage Gate' is met (checking for the presence of test files). 2) Verifying the 'Traceability Gate' (checking description for ticket links). 3) checking CI/CD status. "
                    "RETURNS: A JSON object containing the full PR record and a derived list of files associated with the source branch."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pull_request_id": {
                            "type": "string",
                            "description": "REQUIRED. The unique identifier of the Pull Request to inspect."
                        }
                    },
                    "required": ["pull_request_id"]
                }
            }
        }
