import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class ListPullRequests(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: Optional[str] = None,
        work_item_id: Optional[str] = None,
        program_id: Optional[str] = None,
        state: Optional[str] = None,
        author_id: Optional[str] = None,
        time_window_hours: Optional[int] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for pull_requests"
            })
        
        pull_requests = data.get("pull_requests", {})
        
        # Ensure at least one filter is applied
        if not any([repository_id, work_item_id, program_id, state, author_id, time_window_hours is not None]):
            return json.dumps({
                "success": False,
                "error": "At least one search filter must be provided"
            })
        
        if state:
            valid_states = ["draft", "open", "closed", "merged"]
            if state not in valid_states:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid state '{state}'. Must be one of: {', '.join(valid_states)}"
                })
        
        # Setting "Current Time" to align with your system context
        current_time_str = "2026-02-11T23:59:00"
        current_time = datetime.strptime(current_time_str, "%Y-%m-%dT%H:%M:%S")
        
        found_prs = []
        
        for prid, pr in pull_requests.items():
            if repository_id and str(pr.get("repository_id")) != str(repository_id):
                continue
            
            if work_item_id and str(pr.get("work_item_id")) != str(work_item_id):
                continue
            
            if program_id and str(pr.get("project_id")) != str(program_id):
                continue
            
            if state and pr.get("state") != state:
                continue
            
            if author_id and str(pr.get("author_id")) != str(author_id):
                continue
            
            if time_window_hours is not None:
                created_at_str = pr.get("created_at")
                if not created_at_str:
                    continue
                try:
                    pr_time = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%S")
                    time_difference = current_time - pr_time
                    if time_difference > timedelta(hours=time_window_hours):
                        continue
                except ValueError:
                    continue # Skip if date format is corrupted
            
            pr_data = {
                "pull_request_id": str(prid),
                "repository_id": str(pr.get("repository_id", "")) if pr.get("repository_id") is not None else None,
                "pull_request_number": int(pr.get("pull_request_number")) if pr.get("pull_request_number") is not None else None,
                "title": str(pr.get("title", "")) if pr.get("title") is not None else None,
                "description": str(pr.get("description", "")) if pr.get("description") is not None else None,
                "source_branch": str(pr.get("source_branch", "")) if pr.get("source_branch") is not None else None,
                "target_branch": str(pr.get("target_branch", "")) if pr.get("target_branch") is not None else None,
                "state": str(pr.get("state", "")) if pr.get("state") is not None else None,
                "approval_count": int(pr.get("approval_count")) if pr.get("approval_count") is not None else None,
                "author_id": str(pr.get("author_id", "")) if pr.get("author_id") is not None else None,
                "work_item_id": str(pr.get("work_item_id", "")) if pr.get("work_item_id") is not None else None,
                "program_id": str(pr.get("project_id", "")) if pr.get("project_id") is not None else None,
                "created_at": str(pr.get("created_at", "")) if pr.get("created_at") is not None else None,
                "updated_at": str(pr.get("updated_at", "")) if pr.get("updated_at") is not None else None,
                "merged_at": str(pr.get("merged_at", "")) if pr.get("merged_at") is not None else None,
                "closed_at": str(pr.get("closed_at", "")) if pr.get("closed_at") is not None else None
            }
            
            found_prs.append(pr_data)
        
        if not found_prs:
            return json.dumps({
                "success": True,
                "count": 0,
                "pull_requests": []
            })
        
        return json.dumps({
            "success": True,
            "count": int(len(found_prs)),
            "pull_requests": found_prs
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_pull_requests",
                "description": "Lists code pull requests with filters. Use this to check engineering progress on work items, verify code activity in repositories, identify stale or pending PRs, track developer contributions, or assess code review status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "Filter by repository ID"
                        },
                        "work_item_id": {
                            "type": "string",
                            "description": "Filter by work item ID"
                        },
                        "program_id": {
                            "type": "string",
                            "description": "Filter by project ID"
                        },
                        "state": {
                            "type": "string",
                            "description": "Filter by state",
                            "enum": ["draft", "open", "closed", "merged"]
                        },
                        "author_id": {
                            "type": "string",
                            "description": "Filter by author ID"
                        },
                        "time_window_hours": {
                            "type": "integer",
                            "description": "Filter by creation time within last N hours"
                        }
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["repository_id"]},
                        {"required": ["work_item_id"]},
                        {"required": ["program_id"]},
                        {"required": ["state"]},
                        {"required": ["author_id"]},
                        {"required": ["time_window_hours"]}
                    ]
                }
            }
        }
