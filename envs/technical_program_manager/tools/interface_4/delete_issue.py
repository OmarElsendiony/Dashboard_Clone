import json
from typing import Any, Dict

from tau_bench.envs.tool import Tool


class DeleteIssue(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        issue_id: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not issue_id:
            return json.dumps(
                {"success": False, "error": "Delete requires: issue_id"}
            )

        wid = str(issue_id).strip()
        if not wid:
            return json.dumps(
                {"success": False, "error": "Delete requires: issue_id"}
            )

        work_items = data.get("work_items", {})
        sprints = data.get("sprints", {})

        if wid not in work_items:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Issue '{wid}' not found",
                }
            )

        item = work_items[wid]

        # Collect all descendant issue IDs (full subtree)
        descendants = set()
        queue = [wid]
        while queue:
            parent_id = queue.pop(0)
            for child in work_items.values():
                child_id = str(child.get("work_item_id", ""))
                if (
                    child.get("parent_work_item_id") is not None
                    and str(child.get("parent_work_item_id", "")) == parent_id
                    and child_id not in descendants
                ):
                    descendants.add(child_id)
                    queue.append(child_id)

        # Check all descendants are done/closed
        for did in descendants:
            descendant = work_items[did]
            d_status = str(descendant.get("status", ""))
            if d_status not in ["done", "closed"]:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Cannot delete: child issue '{did}' has status '{d_status}'. All child issues must be 'done' or 'closed'.",
                    }
                )

        # Halt if issue is in a sprint with state active or future
        item_sprint_id = item.get("sprint_id")
        if item_sprint_id is not None:
            sprint = sprints.get(str(item_sprint_id))
            if sprint is not None:
                sprint_state = str(sprint.get("state", ""))
                if sprint_state in ["active", "future"]:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Cannot delete: issue is assigned to sprint '{str(sprint.get('sprint_name', ''))}' with state '{sprint_state}'",
                        }
                    )

        # Delete root item and all descendants
        all_to_delete = {wid} | descendants
        deleted_item = work_items.pop(wid)
        for did in descendants:
            work_items.pop(did, None)

        # Cascade cleanup: nullify FK references for ALL deleted items
        incidents = data.get("incidents", {})
        for inc in incidents.values():
            if inc.get("work_item_id") is not None and str(inc.get("work_item_id", "")) in all_to_delete:
                inc["work_item_id"] = None

        pull_requests = data.get("pull_requests", {})
        for pr in pull_requests.values():
            if pr.get("work_item_id") is not None and str(pr.get("work_item_id", "")) in all_to_delete:
                pr["work_item_id"] = None

        channels = data.get("channels", {})
        for ch in channels.values():
            if ch.get("work_item_id") is not None and str(ch.get("work_item_id", "")) in all_to_delete:
                ch["work_item_id"] = None

        # Safety: nullify parent references for any remaining items pointing to deleted items
        for child in work_items.values():
            if child.get("parent_work_item_id") is not None and str(child.get("parent_work_item_id", "")) in all_to_delete:
                child["parent_work_item_id"] = None

        return json.dumps(
            {
                "success": True,
                "message": f"Issue '{str(deleted_item.get('title', ''))}' has been deleted",
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "delete_issue",
                "description": "Deletes an existing issue. If the issue has child issues, all children must be in a terminal state (done/closed); they will be cascade-deleted along with the parent.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "issue_id": {
                            "type": "string",
                            "description": "Unique issue identifier.",
                        },
                    },
                    "required": ["issue_id"],
                },
            },
        }
