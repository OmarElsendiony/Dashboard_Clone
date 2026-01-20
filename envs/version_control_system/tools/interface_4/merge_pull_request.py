import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class MergePullRequest(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        pull_request_id: str,
        decision: str,
        auth_token: str,
        review_dict: Optional[Dict[str, Any]] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        access_tokens = data.get("access_tokens", {})
        pull_requests = data.get("pull_requests", {})
        pull_request_reviews = data.get("pull_request_reviews", {})
        repository_collaborators = data.get("repository_collaborators", {})
        branches = data.get("branches", {})

        VALID_DECISIONS = {"approved", "changes_requested", "commented", "dismissed"}

        decision = decision.lower()
        if decision not in VALID_DECISIONS:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid decision. Must be one of {sorted(VALID_DECISIONS)}",
                }
            )

        def encode(text: str) -> str:
            return base64.b64encode(text.encode("utf-8")).decode("utf-8")

        # --- Authenticate requester ---
        encoded = encode(auth_token)
        token_info = next(
            (t for t in access_tokens.values() if t.get("token_encoded") == encoded),
            None,
        )

        if not token_info:
            return json.dumps(
                {"success": False, "error": "Invalid authentication token"}
            )

        requester_id = token_info["user_id"]

        # --- Validate pull request ---
        pr = pull_requests.get(pull_request_id)
        if not pr:
            return json.dumps({"success": False, "error": "Pull request not found"})

        if pr["status"] not in {"open", "draft"}:
            return json.dumps(
                {"success": False, "error": f"Pull request is already {pr['status']}"}
            )

        repository_id = pr["repository_id"]

        # --- Ensure branches still exist ---
        source_branch = next(
            (
                b
                for b in branches.values()
                if b["repository_id"] == repository_id
                and b["branch_name"] == pr["source_branch"]
            ),
            None,
        )

        target_branch = next(
            (
                b
                for b in branches.values()
                if b["repository_id"] == repository_id
                and b["branch_name"] == pr["target_branch"]
            ),
            None,
        )

        if not source_branch or not target_branch:
            return json.dumps(
                {"success": False, "error": "Source or target branch no longer exists"}
            )

        # --- Authorization ---
        has_permission = any(
            c
            for c in repository_collaborators.values()
            if c["repository_id"] == repository_id
            and c["user_id"] == requester_id
            and c["permission_level"] in {"admin", "write"}
        )

        if not has_permission:
            return json.dumps(
                {
                    "success": False,
                    "error": "Access denied. Admin or write permission required.",
                }
            )

        now = "2026-01-01T23:59:00"

        # --- Create review entry ---
        try:
            next_review_id = str(max(int(k) for k in pull_request_reviews.keys()) + 1)
        except ValueError:
            next_review_id = "1"

        review_entry = {
            "review_id": next_review_id,
            "pull_request_id": pull_request_id,
            "reviewer_id": requester_id,
            "review_state": decision,
            "review_body": (review_dict or {}).get("review_body"),
            "submitted_at": now,
            "created_at": now,
        }

        pull_request_reviews[next_review_id] = review_entry

        # --- Apply decision ---
        action = decision

        if decision == "approved":
            source_commit_sha = source_branch.get("commit_sha")

            if not source_commit_sha:
                return json.dumps(
                    {"success": False, "error": "Source branch has no commits to merge"}
                )

            # Merge = fast-forward target branch
            target_branch["commit_sha"] = source_commit_sha
            target_branch["updated_at"] = now

            pr["status"] = "merged"
            pr["merged_by"] = requester_id
            pr["merged_at"] = now
            pr["closed_at"] = None

            action = "merged"

        elif decision == "changes_requested":
            pr["status"] = "open"  # stays open, blocks merge

        elif decision == "commented":
            pr["status"] = pr["status"]  # no state change

        elif decision == "dismissed":
            pr["status"] = "closed"

        pr["updated_at"] = now

        # --- Persist ---
        pull_requests[pull_request_id] = pr
        data["pull_requests"] = pull_requests
        data["pull_request_reviews"] = pull_request_reviews

        return json.dumps(
            {
                "success": True,
                "action": action,
                "review": review_entry,
                "pull_request": pr,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "merge_pull_request",
                "description": (
                    "Submits a review decision on a pull request and, if approved, "
                    "merges it into the target branch."
                    ""
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pull_request_id": {
                            "type": "string",
                            "description": "The pull request to review and merge.",
                        },
                        "decision": {
                            "type": "string",
                            "description": "Review decision applied to the pull request.Allowed decisions include ('approved', 'changes_requested', 'commented', 'dismissed')",
                        },
                        "auth_token": {
                            "type": "string",
                            "description": "Authentication token of the reviewer.",
                        },
                        "review_dict": {
                            "type": "object",
                            "description": "Optional review metadata (e.g. review_body).",
                        },
                    },
                    "required": ["pull_request_id", "decision", "auth_token"],
                },
            },
        }
