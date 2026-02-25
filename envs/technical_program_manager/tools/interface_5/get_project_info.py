import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetProjectInfo(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        project_id: Optional[str] = None,
        filter_criteria: Optional[Dict[str, Any]] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if project_id is None and filter_criteria is None:
            return json.dumps(
                {
                    "success": False,
                    "error": "Either project_id or filter_criteria is required",
                }
            )

        projects = data.get("projects", {})
        users = data.get("users", {})
        project_members = data.get("project_members", {})
        scope_changes = data.get("scope_changes", {})
        channels = data.get("channels", {})

        # Validate project_id if provided
        validated_project = None
        if project_id is not None:
            project_id_str = str(project_id)
            # Check direct key lookup or scan
            if project_id_str in projects:
                project_data = projects[project_id_str]
                if str(project_data.get("project_id")) == project_id_str:
                    validated_project = project_data.copy()

            if not validated_project:
                for p_data in projects.values():
                    if str(p_data.get("project_id")) == project_id_str:
                        validated_project = p_data.copy()
                        break

            if not validated_project:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Project with ID {project_id} not found",
                    }
                )

        def enrich_project(project_data: Dict[str, Any]) -> Dict[str, Any]:
            """Helper function to enrich a project with owner, members, scope, and channel info"""
            enriched = project_data.copy()
            project_id_str = str(enriched.get("project_id"))

            # 2. Enrich Owner Information
            owner_id = enriched.get("project_owner_user_id")
            if owner_id and str(owner_id) in users:
                owner = users[str(owner_id)]
                enriched["project_owner_name"] = (
                    f"{owner.get('first_name', '')} {owner.get('last_name', '')}".strip()
                )

            # 3. Enrich Membership Information
            members_list = []
            for member_data in project_members.values():
                if str(member_data.get("project_id")) == project_id_str:
                    m_info = {
                        "project_member_id": str(member_data.get("project_member_id")),
                        "user_id": str(member_data.get("user_id")),
                        "joined_at": str(member_data.get("joined_at")),
                    }
                    user_data = users.get(str(member_data.get("user_id")))
                    if user_data:
                        m_info["user_name"] = (
                            f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
                        )
                    members_list.append(m_info)
            enriched["members"] = members_list

            # 4. Relational Lookup
            relevant_scopes = [
                s
                for s in scope_changes.values()
                if str(s.get("project_id")) == project_id_str
            ]

            if relevant_scopes:
                # Prioritize 'approved' status, then sort by time
                relevant_scopes.sort(
                    key=lambda x: (
                        x.get("status") == "approved",
                        x.get("submitted_at"),
                    ),
                    reverse=True,
                )
                latest_scope = relevant_scopes[0]
                enriched["current_scope"] = {
                    "description": latest_scope.get("description"),
                    "status": latest_scope.get("status"),
                    "last_updated": latest_scope.get("submitted_at"),
                }
            else:
                enriched["current_scope"] = None

            # 5. Lookup channel_id from channels
            channel_id = None
            for channel_data in channels.values():
                if str(channel_data.get("project_id")) == project_id_str:
                    channel_id = channel_data.get("channel_id")
                    break

            if channel_id is not None:
                enriched["channel_id"] = channel_id
            else:
                enriched["channel_id"] = None

            return enriched

        # If filter_criteria is provided, use flexible search
        if filter_criteria is not None:
            if not isinstance(filter_criteria, dict):
                return json.dumps(
                    {"success": False, "error": "filter_criteria must be a dictionary"}
                )

            # Convert dictionary to list first
            all_projects = [p_data.copy() for p_data in projects.values()]
            results = []

            # Search through all projects
            for project_data in all_projects:
                # If project_id is provided, filter by project_id first
                if project_id is not None:
                    pr_project_id = project_data.get("project_id")
                    if str(pr_project_id) != str(project_id):
                        continue

                match = True
                for field, value in filter_criteria.items():
                    pr_value = project_data.get(field)

                    if value is None:
                        if pr_value is not None:
                            match = False
                            break
                        continue

                    if pr_value is None:
                        match = False
                        break

                    # Handle string comparison (case-insensitive partial matching)
                    if isinstance(value, str) and isinstance(pr_value, str):
                        if value.lower() not in pr_value.lower():
                            match = False
                            break
                    # Handle exact match (including string/number conversion for IDs)
                    else:
                        if str(pr_value) != str(value):
                            match = False
                            break

                if match:
                    enriched_project = enrich_project(project_data)
                    results.append(enriched_project)

            response = {
                "success": True,
                "count": len(results),
                "projects": results,
                "filter_criteria": filter_criteria,
            }
            if project_id is not None:
                response["project_id"] = project_id
            return json.dumps(response)

        # Legacy behavior: use project_id
        # Enrich the validated project
        enriched_project = enrich_project(validated_project)

        return json.dumps({"success": True, "project": enriched_project})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_project_info",
                "description": "Retrieve complete project information including project_id, project_key, project_name, description, status, project_owner_user_id, project_owner_name, channel_id, members (list of project members with user_id, user_name, project_member_id, and joined_at), created_at, updated_at, and closed_at. Can query by project_id to get a specific project, or use flexible filter_criteria dictionary to search by any field(s) like project_key, project_name, status, project_owner_user_id, etc. Use this to access project details for project management, status checks, closure verification, and project lifecycle tracking.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The project ID to retrieve information for. If provided, returns that specific project. (Legacy parameter, use filter_criteria for flexible searching)",
                        },
                        "filter_criteria": {
                            "type": "object",
                            "description": "Flexible dictionary of field-value pairs to search for projects. Can include any fields like project_key, project_name, status, project_owner_user_id, description, etc. String fields support partial matching (case-insensitive). All criteria must match (AND logic). Example: {'status': 'open', 'project_key': 'SM'} or {'project_owner_user_id': '41'}",
                            "additionalProperties": True,
                        },
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["project_id"]},
                        {"required": ["filter_criteria"]},
                    ],
                },
            },
        }
