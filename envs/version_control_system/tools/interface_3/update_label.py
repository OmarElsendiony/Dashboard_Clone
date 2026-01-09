import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdateLabel(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        label_id: str,
        pr_ids: Optional[Dict[str, str]] = None,
        issue_ids: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Updates a label by adding or removing pull request IDs or issue IDs.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not label_id:
            return json.dumps({"success": False, "error": "label_id is required to update a label"})

        valid_actions = ["add", "remove"]

        # Parse pr_ids if it's a string
        if pr_ids is not None and isinstance(pr_ids, str):
            try:
                pr_ids = json.loads(pr_ids)
            except json.JSONDecodeError:
                return json.dumps({"success": False, "error": "pr_ids must be a dict with format {id: 'add' or 'remove'}"})

        # Parse issue_ids if it's a string
        if issue_ids is not None and isinstance(issue_ids, str):
            try:
                issue_ids = json.loads(issue_ids)
            except json.JSONDecodeError:
                return json.dumps({"success": False, "error": "issue_ids must be a dict with format {id: 'add' or 'remove'}"})

        # Validate pr_ids format
        if pr_ids is not None:
            if not isinstance(pr_ids, dict):
                return json.dumps({"success": False, "error": "pr_ids must be a dict with format {id: 'add' or 'remove'}"})
            for key, value in pr_ids.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    return json.dumps({"success": False, "error": "pr_ids must be a dict with format {id: 'add' or 'remove'}"})
                if value not in valid_actions:
                    return json.dumps({"success": False, "error": f"Invalid action '{value}' for pr_id '{key}'. Valid values: add, remove"})

        # Validate issue_ids format
        if issue_ids is not None:
            if not isinstance(issue_ids, dict):
                return json.dumps({"success": False, "error": "issue_ids must be a dict with format {id: 'add' or 'remove'}"})
            for key, value in issue_ids.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    return json.dumps({"success": False, "error": "issue_ids must be a dict with format {id: 'add' or 'remove'}"})
                if value not in valid_actions:
                    return json.dumps({"success": False, "error": f"Invalid action '{value}' for issue_id '{key}'. Valid values: add, remove"})

        # Check that at least one field is provided for update
        if pr_ids is None and issue_ids is None:
            return json.dumps({"success": False, "error": "At least one field (pr_ids, issue_ids) must be provided for update"})

        labels = data.get("labels", {})
        pull_requests = data.get("pull_requests", {})
        issues = data.get("issues", {})

        # Validate label exists
        if str(label_id) not in labels:
            return json.dumps({"success": False, "error": f"Label with id '{label_id}' not found"})

        label = labels[str(label_id)]

        # Process pr_ids if provided
        if pr_ids is not None:
            # Get existing pr_ids (handle both comma-separated and JSON array formats)
            existing_pr_ids = label.get("pr_ids")
            if existing_pr_ids:
                if isinstance(existing_pr_ids, list):
                    existing_set = set(str(x) for x in existing_pr_ids)
                elif isinstance(existing_pr_ids, str) and existing_pr_ids.startswith("["):
                    try:
                        parsed = json.loads(existing_pr_ids)
                        existing_set = set(str(x) for x in parsed)
                    except json.JSONDecodeError:
                        existing_set = set(existing_pr_ids.split(","))
                else:
                    existing_set = set(str(existing_pr_ids).split(","))
            else:
                existing_set = set()

            for pr_id, action in pr_ids.items():
                if action == "add":
                    if str(pr_id) not in pull_requests:
                        return json.dumps({"success": False, "error": f"Pull request with id '{pr_id}' not found"})
                    existing_set.add(str(pr_id))
                else:  # remove
                    existing_set.discard(str(pr_id))

            if existing_set:
                try:
                    label["pr_ids"] = ",".join(sorted(existing_set, key=lambda x: int(x)))
                except ValueError:
                    label["pr_ids"] = ",".join(sorted(existing_set))
            else:
                label["pr_ids"] = None

        # Process issue_ids if provided
        if issue_ids is not None:
            # Get existing issue_ids (handle both comma-separated and JSON array formats)
            existing_issue_ids = label.get("issue_ids")
            if existing_issue_ids:
                if isinstance(existing_issue_ids, list):
                    existing_set = set(str(x) for x in existing_issue_ids)
                elif isinstance(existing_issue_ids, str) and existing_issue_ids.startswith("["):
                    try:
                        parsed = json.loads(existing_issue_ids)
                        existing_set = set(str(x) for x in parsed)
                    except json.JSONDecodeError:
                        existing_set = set(existing_issue_ids.split(","))
                else:
                    existing_set = set(str(existing_issue_ids).split(","))
            else:
                existing_set = set()

            for issue_id, action in issue_ids.items():
                if action == "add":
                    if str(issue_id) not in issues:
                        return json.dumps({"success": False, "error": f"Issue with id '{issue_id}' not found"})
                    existing_set.add(str(issue_id))
                else:  # remove
                    existing_set.discard(str(issue_id))

            if existing_set:
                try:
                    label["issue_ids"] = ",".join(sorted(existing_set, key=lambda x: int(x)))
                except ValueError:
                    label["issue_ids"] = ",".join(sorted(existing_set))
            else:
                label["issue_ids"] = None

        return json.dumps({"success": True, "result": label})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_label",
                "description": "Updates a label by adding or removing pull request IDs or issue IDs.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "label_id": {
                            "type": "string",
                            "description": "The unique identifier of the label to update."
                        },
                        "pr_ids": {
                            "type": "object",
                            "description": "A dictionary of pull request IDs with their actions. Format: {id: action} where action is 'add' or 'remove'. Optional."
                        },
                        "issue_ids": {
                            "type": "object",
                            "description": "A dictionary of issue IDs with their actions. Format: {id: action} where action is 'add' or 'remove'. Optional."
                        }
                    },
                    "required": ["label_id"]
                }
            }
        }
