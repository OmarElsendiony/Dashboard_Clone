import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ModerateIssue(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        issue_id: int,
        action: str,
        actor_id: Optional[int] = None,
        repository_id: Optional[int] = None,
        lock_reason: Optional[str] = None,
        audit_ticket: Optional[bool] = True,
        enforce_awaiting_info: Optional[bool] = True,
        min_failure_description_length: Optional[int] = 20,
        ticket_id: Optional[str] = None,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not issue_id:
            return json.dumps({"success": False, "error": "Missing Argument: 'issue_id' is required."})

        if not action:
            return json.dumps({"success": False, "error": "Missing Argument: 'action' is required."})

        if not isinstance(action, str) or not action.strip():
            return json.dumps({"success": False, "error": "Invalid Argument: action must be a non-empty string."})

        action_norm = action.strip().lower()
        valid_actions = ["lock", "unlock", "audit"]
        if action_norm not in valid_actions:
            return json.dumps({
                "success": False,
                "error": f"Invalid Argument: action must be one of {valid_actions}."
            })

        if not isinstance(issue_id, int):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: issue_id must be an integer."
            })

        if audit_ticket is None:
            audit_ticket = True
        if not isinstance(audit_ticket, bool):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: audit_ticket must be a boolean."
            })

        if enforce_awaiting_info is None:
            enforce_awaiting_info = True
        if not isinstance(enforce_awaiting_info, bool):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: enforce_awaiting_info must be a boolean."
            })

        if min_failure_description_length is None:
            min_failure_description_length = 20
        if not isinstance(min_failure_description_length, int) or min_failure_description_length <= 0:
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: min_failure_description_length must be a positive integer."
            })

        if ticket_id is not None and (not isinstance(ticket_id, str) or not ticket_id.strip()):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: ticket_id must be a non-empty string when provided."
            })

        if lock_reason is not None and (not isinstance(lock_reason, str) or not lock_reason.strip()):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: lock_reason must be a non-empty string when provided."
            })

        issues = data.get("issues", {})
        repositories = data.get("repositories", {})
        users = data.get("users", {})
        tickets = data.get("tickets", {})
        ticket_notes = data.get("ticket_notes", {})

        if not isinstance(issues, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'issues' must be a dictionary"})

        if not isinstance(repositories, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'repositories' must be a dictionary"})

        if not isinstance(users, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'users' must be a dictionary"})

        if not isinstance(tickets, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'tickets' must be a dictionary"})

        if not isinstance(ticket_notes, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'ticket_notes' must be a dictionary"})

        if actor_id is not None:
            if not isinstance(actor_id, int):
                return json.dumps({
                    "success": False,
                    "error": "Invalid Argument: actor_id must be an integer when provided."
                })
            if str(actor_id) not in users:
                return json.dumps({
                    "success": False,
                    "error": f"Authorization Error: actor_id '{actor_id}' not found."
                })

        if repository_id is not None:
            if not isinstance(repository_id, int):
                return json.dumps({
                    "success": False,
                    "error": "Invalid Argument: repository_id must be an integer when provided."
                })
            if str(repository_id) not in repositories:
                return json.dumps({
                    "success": False,
                    "error": f"Foreign Key Error: repository_id '{repository_id}' not found."
                })

        issue_key = str(issue_id)
        issue = issues.get(issue_key)

        if issue is None:
            issue = issues.get(issue_id) if isinstance(issue_id, int) else None

        if issue is None:
            for v in issues.values():
                if isinstance(v, dict) and str(v.get("issue_id", "")).strip() == issue_key:
                    issue = v
                    break

        if issue is None:
            return json.dumps({
                "success": False,
                "error": f"Not Found Error: issue_id '{issue_id}' not found."
            })

        if repository_id is not None and str(issue.get("repository_id", "")).strip() != str(repository_id).strip():
            return json.dumps({
                "success": False,
                "error": f"Not Found Error: issue_id '{issue_id}' not found in repository '{repository_id}'."
            })

        timestamp = "2026-02-02 23:59:00"

        audit_result = {
            "performed": False,
            "passed": None,
            "missing": [],
            "ticket_id": "",
            "ticket_status_before": "",
            "ticket_status_after": "",
            "enforced_awaiting_info": False,
        }

        if audit_ticket:
            target_ticket_ref = ""
            if ticket_id is not None:
                target_ticket_ref = ticket_id.strip()
            else:
                ot = issue.get("originating_ticket_id")
                if ot is not None:
                    target_ticket_ref = str(ot).strip()

            if not target_ticket_ref:
                return json.dumps({
                    "success": False,
                    "error": "Not Found Error: No ticket reference available for content audit."
                })

            ticket_obj = None
            if target_ticket_ref in tickets and isinstance(tickets.get(target_ticket_ref), dict):
                ticket_obj = tickets.get(target_ticket_ref)

            if ticket_obj is None:
                for tv in tickets.values():
                    if not isinstance(tv, dict):
                        continue
                    if str(tv.get("ticket_id", "")).strip() == target_ticket_ref:
                        ticket_obj = tv
                        break
                    if str(tv.get("ticket_number", "")).strip() == target_ticket_ref:
                        ticket_obj = tv
                        break

            if ticket_obj is None:
                return json.dumps({
                    "success": False,
                    "error": f"Not Found Error: ticket '{target_ticket_ref}' not found for content audit."
                })

            canonical_ticket_id = str(ticket_obj.get("ticket_id", "")).strip()
            if not canonical_ticket_id:
                canonical_ticket_id = target_ticket_ref

            desc = str(ticket_obj.get("description", "") or "")
            desc_stripped = desc.strip()

            failure_ok = len(desc_stripped) >= int(min_failure_description_length)

            scope_ok = False
            desc_lower = desc.lower()
            if "scope:" in desc_lower:
                p = desc_lower.find("scope:")
                after = desc[p + 6:]
                first_line = after.splitlines()[0] if after is not None else ""
                v = str(first_line).strip()
                if v:
                    if "/" in v or "global" in v.lower():
                        scope_ok = True

            if not scope_ok:
                for nv in ticket_notes.values():
                    if not isinstance(nv, dict):
                        continue
                    if str(nv.get("ticket_id", "")).strip() != canonical_ticket_id:
                        continue
                    body = str(nv.get("body", "") or "")
                    title = str(nv.get("title", "") or "")
                    combined = (title + "\n" + body).lower()
                    if "scope:" in combined:
                        p2 = combined.find("scope:")
                        after2 = combined[p2 + 6:]
                        first_line2 = after2.splitlines()[0] if after2 is not None else ""
                        v2 = str(first_line2).strip()
                        if v2:
                            if "/" in v2 or "global" in v2.lower():
                                scope_ok = True
                                break

            missing = []
            if not failure_ok:
                missing.append("failure_description")
            if not scope_ok:
                missing.append("scope")

            before_status = str(ticket_obj.get("status", "") or "")
            after_status = before_status
            enforced = False

            if len(missing) > 0 and enforce_awaiting_info:
                if before_status != "awaiting_info":
                    ticket_obj["status"] = "awaiting_info"
                    ticket_obj["updated_at"] = timestamp
                    after_status = "awaiting_info"
                    enforced = True

            audit_result = {
                "performed": True,
                "passed": len(missing) == 0,
                "missing": missing,
                "ticket_id": canonical_ticket_id,
                "ticket_status_before": before_status,
                "ticket_status_after": after_status,
                "enforced_awaiting_info": enforced,
            }

        if action_norm == "audit":
            return json.dumps({
                "success": True,
                "issue": issue,
                "action": "audit",
                "audit": audit_result,
                "message": "Ticket content audit completed."
            })

        current_locked = False
        if isinstance(issue.get("conversation_locked"), bool):
            current_locked = bool(issue.get("conversation_locked"))
        elif isinstance(issue.get("locked"), bool):
            current_locked = bool(issue.get("locked"))
        else:
            cs = issue.get("conversation_status")
            if isinstance(cs, str) and cs.strip().lower() == "locked":
                current_locked = True

        if action_norm == "lock":
            if current_locked is True:
                return json.dumps({
                    "success": False,
                    "error": "Unconditional Write Detected",
                    "message": f"No-Op: Issue '{issue_id}' conversation is already locked.",
                    "issue": issue,
                    "action": "lock",
                    "audit": audit_result
                })

            issue["conversation_locked"] = True
            issue["conversation_status"] = "locked"
            if actor_id is not None:
                issue["conversation_locked_by"] = actor_id
            if lock_reason is not None:
                issue["conversation_lock_reason"] = lock_reason.strip()
            issue["conversation_locked_at"] = timestamp
            issue["updated_at"] = timestamp

            return json.dumps({
                "success": True,
                "issue": issue,
                "action": "lock",
                "already_locked": False,
                "audit": audit_result,
                "message": "Issue conversation locked successfully."
            })

        if action_norm == "unlock":
            if current_locked is False:
                return json.dumps({
                    "success": False,
                    "error": "Unconditional Write Detected",
                    "message": f"No-Op: Issue '{issue_id}' conversation is already unlocked.",
                    "issue": issue,
                    "action": "unlock",
                    "audit": audit_result
                })

            issue["conversation_locked"] = False
            issue["conversation_status"] = "unlocked"
            issue["updated_at"] = timestamp

            if "conversation_locked_at" in issue:
                issue["conversation_locked_at"] = ""
            if "conversation_lock_reason" in issue:
                issue["conversation_lock_reason"] = ""
            if "conversation_locked_by" in issue:
                issue["conversation_locked_by"] = ""

            return json.dumps({
                "success": True,
                "issue": issue,
                "action": "unlock",
                "already_unlocked": False,
                "audit": audit_result,
                "message": "Issue conversation unlocked successfully."
            })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "moderate_issue",
                "description": (
                    "Applies repository issue conversation moderation while enforcing a policy-driven content audit on the originating Zendesk ticket."

                    "PURPOSE: Synchronizes GitHub-style issue thread control with support ticket quality standards to ensure engineering teams only handle well-documented incidents."

                    "WHEN TO USE: When you need to freeze (lock) or re-open (unlock) a discussion thread, or when the workflow must verify that the linked ticket contains a concrete failure description and a valid Scope field before allowing further escalation."

                    "RETURNS: Both the moderation result (locked/unlocked) and the ticket audit outcome, indicating whether the upstream ticket is compliant with Incident Brief standards or has been transitioned to an 'awaiting-information' posture."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "issue_id": {
                            "type": "integer",
                            "description": "The unique ID of the repository issue to moderate."
                        },
                        "action": {
                            "type": "string",
                            "enum": ["lock", "unlock", "audit"],
                            "description": "Conversation moderation or audit action to apply."
                        },
                        "actor_id": {
                            "type": "integer",
                            "description": "Identifier of the agent/moderator applying the action (optional )"
                        },
                        "repository_id": {
                            "type": "integer",
                            "description": "Restrict moderation to a specific repository (optional )"
                        },
                        "lock_reason": {
                            "type": "string",
                            "description": "Reason for locking the issue conversation (optional )"
                        },
                        "audit_ticket": {
                            "type": "boolean",
                            "description": "Perform linked Zendesk ticket content audit (optional )"
                        },
                        "enforce_awaiting_info": {
                            "type": "boolean",
                            "description": "Set ticket status to awaiting_info when required content is missing (optional )"
                        },
                        "min_failure_description_length": {
                            "type": "integer",
                            "description": "Minimum length required for a valid failure description in the ticket body (optional )"
                        },
                        "ticket_id": {
                            "type": "string",
                            "description": "Explicit ticket identifier to audit instead of issue-origin linkage (optional )"
                        }
                    },
                    "required": ["issue_id", "action"]
                }
            }
        }
