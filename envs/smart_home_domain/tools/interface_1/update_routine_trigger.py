import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class UpdateRoutineTrigger(Tool):
    """
    Update a routine trigger's attributes in the routine_trigger_attributes table.
    - Requires routine_id, trigger_id, and new_attributes.
    - Validates that routine, trigger, and attributes exist.
    - Updates attribute_value and comparison_operator for specified attributes.
    - Cannot update attribute_id, trigger_id, or created_at.
    - new_attributes format: {attribute_name: {field: value, ...}}
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        routine_id: str,
        trigger_id: str,
        new_attributes: Dict[str, Any]
    ) -> str:
        """
        Update a routine trigger's attributes in the routine_trigger_attributes table.
        
        Args:
            data: The data dictionary containing routines, routine_triggers, and routine_trigger_attributes
            routine_id: The ID of the routine
            trigger_id: The ID of the trigger
            new_attributes: Dictionary of new attribute values to apply (can contain multiple attributes)
            
        Returns:
            JSON string with success status and updated attribute information
        """
        # Basic input validation
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'data' must be a dict"
            })

        routines_dict = data.get("routines", {})
        if not isinstance(routines_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid routines container: expected dict at data['routines']"
            })

        routine_triggers_dict = data.get("routine_triggers", {})
        if not isinstance(routine_triggers_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid routine_triggers container: expected dict at data['routine_triggers']"
            })

        routine_trigger_attributes_dict = data.get("routine_trigger_attributes", {})
        if not isinstance(routine_trigger_attributes_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid routine_trigger_attributes container: expected dict at data['routine_trigger_attributes']"
            })

        # Validate required fields
        if routine_id is None:
            return json.dumps({"success": False, "error": "routine_id is required"})

        if trigger_id is None:
            return json.dumps({"success": False, "error": "trigger_id is required"})

        if not isinstance(new_attributes, dict):
            return json.dumps({
                "success": False,
                "error": "new_attributes must be a dictionary"
            })

        if not new_attributes:
            return json.dumps({
                "success": False,
                "error": "new_attributes dictionary cannot be empty"
            })

        # Convert to strings for consistent comparison
        routine_id_str = str(routine_id)
        trigger_id_str = str(trigger_id)

        # Validate routine exists
        if routine_id_str not in routines_dict:
            return json.dumps({
                "success": False,
                "error": f"Routine not found: '{routine_id_str}'"
            })

        # Validate trigger exists
        if trigger_id_str not in routine_triggers_dict:
            return json.dumps({
                "success": False,
                "error": f"Trigger not found: '{trigger_id_str}'"
            })

        trigger_data = routine_triggers_dict[trigger_id_str]

        # Validate trigger belongs to the specified routine
        if str(trigger_data.get("routine_id")) != routine_id_str:
            return json.dumps({
                "success": False,
                "error": f"Trigger '{trigger_id_str}' does not belong to routine '{routine_id_str}'"
            })

        # Find all attributes that belong to this trigger
        trigger_attributes = {}
        for attr_id, attr_data in routine_trigger_attributes_dict.items():
            if str(attr_data.get("trigger_id")) == trigger_id_str:
                attr_name = attr_data.get("attribute_name")
                if attr_name:
                    trigger_attributes[attr_name] = (attr_id, attr_data)

        # Validate that protected fields are not in new_attributes
        protected_fields = ["attribute_id", "trigger_id", "created_at"]
        for field in protected_fields:
            if field in new_attributes:
                return json.dumps({
                    "success": False,
                    "error": f"Cannot update protected field: '{field}'"
                })

        # Valid comparison operators
        valid_operators = ["equals", "greater_than", "less_than", "greater_equal", "less_equal"]

        # Validate new_attributes structure
        # new_attributes should be a dict where each key is an attribute_name
        # and value is a dict with fields to update
        updated_attributes = []
        
        for attr_name, attr_updates in new_attributes.items():
            # Check if this attribute exists for the trigger
            if attr_name not in trigger_attributes:
                return json.dumps({
                    "success": False,
                    "error": f"Attribute '{attr_name}' not found for trigger '{trigger_id_str}'"
                })
            
            if not isinstance(attr_updates, dict):
                return json.dumps({
                    "success": False,
                    "error": f"Updates for attribute '{attr_name}' must be a dictionary"
                })
            
            # Validate update fields
            allowed_fields = ["attribute_value", "comparison_operator"]
            for field, value in attr_updates.items():
                if field not in allowed_fields:
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid update field: '{field}' for attribute '{attr_name}'. Allowed fields: {', '.join(allowed_fields)}"
                    })
                
                if field == "comparison_operator" and value not in valid_operators:
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid comparison_operator: '{value}'. Must be one of {valid_operators}"
                    })
            
            # Apply updates to the attribute
            attr_id, attr_data = trigger_attributes[attr_name]
            for field, value in attr_updates.items():
                attr_data[field] = value
            
            updated_attributes.append({
                "attribute_id": attr_id,
                "attribute_name": attr_name,
                "updated_fields": list(attr_updates.keys())
            })

        return json.dumps({
            "success": True,
            "message": f"Updated {len(updated_attributes)} attribute(s) for trigger '{trigger_id_str}'",
            "updated_attributes": updated_attributes
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """
        Tool schema for function-calling.
        """
        return {
            "type": "function",
            "function": {
                "name": "update_routine_trigger",
                "description": (
                    "Update a routine trigger's attributes in the routine_trigger_attributes table. "
                    "Requires routine_id, trigger_id, and new_attributes. "
                    "Validates that routine, trigger, and attributes exist. "
                    "new_attributes is a dict mapping attribute_name to update fields. "
                    "Allowed update fields per attribute: attribute_value, comparison_operator. "
                    "Cannot update attribute_id, trigger_id, or created_at. "
                    "Valid comparison operators: equals, greater_than, less_than, greater_equal, less_equal."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "routine_id": {
                            "type": "string",
                            "description": "The ID of the routine (required)."
                        },
                        "trigger_id": {
                            "type": "string",
                            "description": "The ID of the trigger (required)."
                        },
                        "new_attributes": {
                            "type": "object",
                            "description": (
                                "Dictionary mapping attribute names to their updates. "
                                "Format: {attribute_name: {field: value, ...}}. "
                                "Allowed update fields: attribute_value, comparison_operator."
                            ),
                            "additionalProperties": True
                        }
                    },
                    "required": ["routine_id", "trigger_id", "new_attributes"],
                },
            },
        }

