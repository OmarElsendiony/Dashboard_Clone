import os
import json
import ast
import re
from typing import Dict, Any
from flask import Blueprint, render_template, request, jsonify, session, g, Response

task_framework_bp = Blueprint('task_framework', __name__)

# Base path for environments - resolved at module load time (safe, no user input)
ENVS_BASE_PATH = os.path.abspath("envs")


def validate_path_component(component):
    """
    Validate a path component (like environment or interface name) to prevent path traversal.
    Returns True if the component is safe, False otherwise.
    """
    if not component or not isinstance(component, str):
        return False
    # Check for path traversal patterns
    if '..' in component or '/' in component or '\\' in component:
        return False
    # Check for null bytes
    if '\x00' in component:
        return False
    # Only allow alphanumeric characters, underscores, and hyphens
    if not re.match(r'^[a-zA-Z0-9_-]+$', component):
        return False
    return True


def safe_join_path(base_path, *components):
    """
    Safely join path components after validating each one.
    Returns the joined path if all components are valid, None otherwise.
    All components must pass validate_path_component check.
    """
    for component in components:
        if not validate_path_component(component):
            return None
    # All components validated - safe to join
    return os.path.join(base_path, *components)


def validate_filename(filename):
    """
    Validate a filename from directory listing to ensure it's safe.
    Returns True if the filename is safe to use, False otherwise.
    """
    if not filename or not isinstance(filename, str):
        return False
    # Check for path traversal patterns
    if '..' in filename or '/' in filename or '\\' in filename:
        return False
    # Check for null bytes
    if '\x00' in filename:
        return False
    # Filename should not be empty or just dots
    if filename in ('.', '..'):
        return False
    return True


def safe_open_file(base_dir, filename, mode='r'):
    """
    Safely open a file within a base directory after validating the filename.
    Returns file handle if safe, raises ValueError if unsafe.
    """
    if not validate_filename(filename):
        raise ValueError(f"Invalid filename: {filename}")

    file_path = os.path.join(base_dir, filename)

    # Verify the resolved path is still within base_dir
    abs_base = os.path.abspath(base_dir)
    abs_file = os.path.abspath(file_path)

    if not abs_file.startswith(abs_base + os.sep):
        raise ValueError(f"Path traversal detected: {filename}")

    return open(abs_file, mode)



######################## UTILITY FUNCTIONS ##################################
def ast_to_python_value(node):
    """Convert AST node to Python value."""
    if isinstance(node, ast.Constant):  # Python 3.8+
        return node.value
    elif isinstance(node, ast.Str):  # Python < 3.8
        return node.s
    elif isinstance(node, ast.Num):  # Python < 3.8
        return node.n
    elif isinstance(node, ast.List):
        return [ast_to_python_value(item) for item in node.elts]
    elif isinstance(node, ast.Dict):
        result = {}
        for key, value in zip(node.keys, node.values):
            result[ast_to_python_value(key)] = ast_to_python_value(value)
        return result
    elif isinstance(node, ast.Name):
        # For variable names, we can't resolve them without execution
        # Return the name as a string for now
        return f"<variable: {node.id}>"
    else:
        # For other node types, return a string representation
        return f"<{type(node).__name__}>"


def extract_method_from_ast(source_code: str, method_name: str) -> str:
    tree = ast.parse(source_code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == method_name:
            start = node.lineno - 1
            end = node.end_lineno
            return '\n'.join(source_code.splitlines()[start:end])
    return None


def extract_file_info(file_path: str) -> Dict[str, Any]:
    """
    Extract function information from a Python file containing a Tool class with get_info method.
    The file_path should be an absolute path that has already been validated.
    """
    try:
        # Ensure the path is absolute and doesn't contain traversal patterns
        if not os.path.isabs(file_path):
            return {"error": "File path must be absolute"}
        if '..' in file_path:
            return {"error": "Invalid file path"}

        # Read the file content
        with open(file_path, "r") as file:
            content = file.read()
        
        imports = []
        import_pattern = re.compile(r'^\s*import\s+(\w+)', re.MULTILINE)
        from_import_pattern =  re.compile(r'^\s*from\s+([\w\.]+)\s+import\s+((?:\w+\s*,\s*)*\w+)', re.MULTILINE)
        
        for match in import_pattern.finditer(content):
            imports.append(match.group(0).strip())
        for match in from_import_pattern.finditer(content):
            if match.group(1) == "tau_bench.envs.tool":
                # Skip tau_bench.envs.tool import
                continue
            imports.append(match.group(0).strip())
        
        tree = ast.parse(content)
        
        tool_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == 'Tool':
                        tool_class = node
                        # break
            if isinstance(node, ast.FunctionDef) and node.name == "invoke":
                start = node.lineno - 1
                end = node.end_lineno
                invoke_method = '\n'.join(content.splitlines()[start:end])
                # if tool_class:
                #     break
        
        if not tool_class:
            return {"error": "No Tool class found"}
        
        if not invoke_method:
            return {"error": "No invoke method found in Tool class"}
        
        # Find the get_info method
        get_info_method = None
        for node in tool_class.body:
            if isinstance(node, ast.FunctionDef) and node.name == 'get_info':
                get_info_method = node
                break
        
        if not get_info_method:
            return {"error": "No get_info method found"}
        
        return_dict = None
        for node in ast.walk(get_info_method):
            if isinstance(node, ast.Return):
                return_dict = node.value
                break
        
        if not return_dict:
            return {"error": "No return dictionary found in get_info method"}
        
        parsed_dict = ast_to_python_value(return_dict)
        function_info = {}
        
        if isinstance(parsed_dict, dict) and 'function' in parsed_dict:
            func_info = parsed_dict['function']
            if isinstance(func_info, dict):
                function_info = {
                    'name': func_info.get('name', ''),
                    'description': func_info.get('description', ''),
                    'parameters': func_info.get('parameters', {}).get('properties', {}),
                    'required': func_info.get('parameters', {}).get('required', [])
                }

        return function_info, invoke_method, imports
        
    except Exception as e:
        return {"error": f"Failed to process file: {str(e)}"}
######################## END UTILITY FUNCTIONS ##############################


def create_tools_class(imports_set, invoke_methods):
    # Create the class dynamically in memory
    imports_code = '\n'.join(sorted(imports_set))
    
    # Build the class definition as a string
    class_code = f"""
{imports_code}

class Tools:
"""
    for invoke_method in invoke_methods:
        class_code += ("    @staticmethod\n" + invoke_method + "\n\n")
    # Execute the code and return the class
    namespace = {}
    exec(class_code, namespace)
    # return namespace['Tools']
    # session["tools_class_code"] = class_code 
    return namespace['Tools']

def arguments_processing(arguments):
    cleaned_arguments = {}
    for argument, argument_value in arguments.items():
        # Skip empty values
        if argument_value == '':
            continue

        # Skip IDs (do not modify or parse)
        # if "id" == argument.lower() or "_id" in argument.lower() or "_by" in argument.lower() or "name" in argument.lower() or "_to" in argument.lower() or argument == "new_value" or argument == "old_value":
        #     cleaned_arguments[argument] = argument_value
        #     continue
        # Try to parse as JSON first (for objects/arrays)
        if isinstance(argument_value, str) and (argument_value.startswith('{') or argument_value.startswith('[')):
            try:
                cleaned_arguments[argument] = json.loads(argument_value)
                continue
            except (json.JSONDecodeError, ValueError):
                pass  # Fall through to literal_eval
        else:
            cleaned_arguments[argument] = argument_value
        # Try to evaluate literal (e.g., convert "True" → True, "123" → 123)
        # try:
        #     cleaned_arguments[argument] = ast.literal_eval(argument_value)
        # except (ValueError, SyntaxError):
        #     cleaned_arguments[argument] = argument_value

    return cleaned_arguments


@task_framework_bp.route('/task-framework', strict_slashes=False, methods=["POST", "GET"])
def task_framework():
    return render_template('task_framework.html')



@task_framework_bp.route('/choose_env_interface', strict_slashes=False, methods=["POST", "GET"])
def env_interface():
    """ Endpoint to handle environment and interface selection """
    if request.method == "POST":
        try:
            passed_inputs = request.get_json()
            
            environment = passed_inputs.get('environment') if passed_inputs else None
            interface = passed_inputs.get('interface') if passed_inputs else None

            # Validate environment and interface to prevent path traversal attacks
            if not environment or not validate_path_component(environment):
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid environment name'
                }), 400
            if not interface or not validate_path_component(interface):
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid interface name'
                }), 400

            # global last_environment, last_interface, data

            # print(environment, session.get("environment"))
            if environment != session.get("environment"):
                g.data.clear()
                session["environment"] = environment
                session["interface"] = interface

            # print(session["environment"], session["interface"])
            if environment and interface:
                # Construct path safely using validated components
                # interface is prefixed with "interface_" which is safe
                interface_dir = f"interface_{interface}"
                INTERFACE_PATH = safe_join_path(ENVS_BASE_PATH, environment, "tools", interface_dir)

                if INTERFACE_PATH is None:
                    return jsonify({
                        'status': 'error',
                        'message': 'Invalid path specified'
                    }), 400

                if not os.path.isdir(INTERFACE_PATH):
                    return jsonify({
                        'status': 'error',
                        'message': 'Environment or interface not found'
                    }), 404

                API_files = os.listdir(INTERFACE_PATH)
                invoke_methods = []
                functionsInfo = []
                importsSet = set()
                for api_file in API_files:
                    # Validate filename before using it
                    if not validate_filename(api_file):
                        continue
                    if api_file.endswith(".py") and not api_file.startswith("__"):
                        # Construct path and verify it stays within base directory
                        file_path = os.path.join(INTERFACE_PATH, api_file)
                        abs_interface = os.path.abspath(INTERFACE_PATH)
                        abs_file = os.path.abspath(file_path)
                        if not abs_file.startswith(abs_interface + os.sep):
                            continue  # Skip files that would escape the directory
                        try:
                            function_info, invoke_method, imports = extract_file_info(abs_file)
                            # print(f"Extracted function info: {function_info}")
                            # if not function_info:
                            #     print(f"No function info found in {api_file}, skipping.")
                            #     continue
                            importsSet.update(imports)
                            invoke_method = invoke_method.replace("invoke", function_info.get('name', 'invoke')+"_invoke")
                            invoke_methods.append(invoke_method)
                            functionsInfo.append(function_info)

                        except SyntaxError as e:
                            print(f"Syntax error in {api_file}: {e}")
                        except Exception as e:
                            print(f"Error processing {api_file}: {e}")
                
                # temp_dir = "/tmp"
                # tools_file_path = os.path.join(temp_dir, "tools.py")
                # with open(tools_file_path, "w") as new_file:
                #     new_file.write('\n'.join(sorted(importsSet)) + "\n\n")
                #     new_file.write("class Tools:\n")
                #     for invoke_method in invoke_methods:
                #         new_file.write("    @staticmethod\n" + invoke_method + "\n\n")
                session["imports_set"] = importsSet
                session["invoke_methods"] = invoke_methods
                session["actions"] = []
                # print("Imports set:", session["imports_set"])
                return jsonify({
                    'status': 'success',
                    'message': 'Environment and interface selected successfully',
                    'functions_info': functionsInfo,
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Missing environment or interface data'
                }), 400
                
        except Exception as e:
            # print(f"Error processing request: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'{str(e)}'
            }), 500
    
    # Handle GET requests
    elif request.method == "GET":
        return jsonify({
            'status': 'success',
            'message': 'Choose environment and interface endpoint is working'
        })

def execute_api_utility(api_name, arguments):
    tools_instance = create_tools_class(session.get("imports_set", []), session.get("invoke_methods", []))
    # print('executing ...')
    arguments = arguments_processing(arguments)
    if hasattr(tools_instance, api_name):
        # try:
            # print(g.data)
            # Dynamically call the method with the provided arguments
            result = getattr(tools_instance, api_name)(data=g.data, **arguments)
            return result
            # print(f"Result from API {api_name}: {result}")
            # session["actions"].append({
            #     'api_name': api_name,
            #     'arguments': arguments
            # })
    #         return jsonify({
    #             'output': json.loads(result) if isinstance(result, str) else result
    #         }), 200
    #     except Exception as e:
    #         print(f"Error executing API {api_name}: {str(e)}")
    #         return jsonify({
    #             'status': 'error',
    #             'message': f'Failed to execute API: {str(e)}'
    #         }), 500
    # else:
    #     return jsonify({
    #         'status': 'error',
    #         'message': f'API {api_name} not found'
    #     }), 404

# def convert_floats_to_strings(obj):
#     """Recursively convert all float values to strings with .0 preserved"""
#     if isinstance(obj, dict):
#         return {k: convert_floats_to_strings(v) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         return [convert_floats_to_strings(item) for item in obj]
#     elif isinstance(obj, float):
#         # Check if it's a whole number
#         if obj.is_integer():
#             return f"{int(obj)}.0"
#         else:
#             return str(obj)
#     return obj

# def detect_float_fields(obj, parent_key='', float_fields=None):
#     """Recursively detect which fields are floats"""
#     if float_fields is None:
#         float_fields = set()
    
#     if isinstance(obj, dict):
#         for key, value in obj.items():
#             if isinstance(value, float):
#                 float_fields.add(key)
#             if isinstance(value, (dict, list)):
#                 detect_float_fields(value, key, float_fields)
#     elif isinstance(obj, list):
#         for item in obj:
#             detect_float_fields(item, parent_key, float_fields)
    
#     return float_fields

def detect_float_fields(obj, parent_key='', float_fields=None):
    """Recursively detect which fields are floats, including in nested structures"""
    if float_fields is None:
        float_fields = set()
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, float):
                # Add the field name (not the parent key)
                float_fields.add(key)
            if isinstance(value, (dict, list)):
                # Recursively check nested structures
                detect_float_fields(value, key, float_fields)
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                # For items in arrays, continue recursion without changing parent_key
                detect_float_fields(item, parent_key, float_fields)
            elif isinstance(item, float):
                # If the list contains float primitives, track using parent_key
                if parent_key:
                    float_fields.add(parent_key)
    
    return float_fields

def apply_float_fields(obj, float_fields, current_path=''):
    """
    Recursively convert integers to floats for fields specified in float_fields.
    
    Args:
        obj: The object to process (dict or list)
        float_fields: List of field paths like ['holding_data.quantity']
        current_path: Current path in the object hierarchy (used internally)
    
    Returns:
        Modified object with integers converted to floats
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            # Build the full path for this key
            full_path = f"{current_path}.{key}" if current_path else key
            
            # Check if this field should be converted to float
            should_be_float = False
            for float_field in float_fields:
                # Match full path or check if the field name matches at the end of path
                if full_path == float_field:
                    should_be_float = True
                    break
                # Also check if current path + key matches the float_field
                elif float_field.endswith(f".{key}"):
                    parent_path = '.'.join(float_field.split('.')[:-1])
                    if current_path == parent_path:
                        should_be_float = True
                        break
            
            # Convert to float if needed
            if should_be_float and isinstance(value, int):
                obj[key] = float(value)
                # print(f"  ✓ Converted {full_path}: {value} (int) -> {float(value)} (float)")
            
            # Recursively process nested structures
            if isinstance(value, dict):
                apply_float_fields(value, float_fields, full_path)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        apply_float_fields(item, float_fields, f"{full_path}[{i}]")
    
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, dict):
                apply_float_fields(item, float_fields, f"{current_path}[{i}]")
    
    return obj


@task_framework_bp.route('/execute_api', strict_slashes=False, methods=["GET", "POST"])
def execute_api():
    # global data, last_environment, last_interface  # Add global declaration
    if request.method != "POST":
        return jsonify({
            'status': 'error',
            'message': 'Only POST requests are allowed'
        }), 405

    passed_data = request.get_json()
    # print(passed_data)
    # print(passed_data.get('environment'))
    environment = passed_data.get('environment', session.get("environment"))

    # Validate environment to prevent path traversal attacks
    if not environment or not validate_path_component(environment):
        return jsonify({
            'status': 'error',
            'message': 'Invalid environment name'
        }), 400

    # Construct path safely using validated component
    DATA_PATH = safe_join_path(ENVS_BASE_PATH, environment, "data")

    if DATA_PATH is None:
        return jsonify({
            'status': 'error',
            'message': 'Invalid path specified'
        }), 400

    if not os.path.isdir(DATA_PATH):
        return jsonify({
            'status': 'error',
            'message': 'Data directory not found'
        }), 404

    data_files = os.listdir(DATA_PATH)
    # print("Loaded data:")
    abs_data_path = os.path.abspath(DATA_PATH)
    for data_file in data_files:
        # Validate filename before using it
        if not validate_filename(data_file):
            continue
        if data_file.endswith(".json"):
            data_file_path = os.path.join(DATA_PATH, data_file)
            # Verify the path stays within the data directory
            abs_file_path = os.path.abspath(data_file_path)
            if not abs_file_path.startswith(abs_data_path + os.sep):
                continue  # Skip files that would escape the directory
            with open(abs_file_path, "r") as file:
                g.data[data_file.split('.')[0]] = json.load(file)
    
    for action in session.get("actions", []):
        # print('session:', session.get("actions"))
        api_name = action.get('api_name')
        execute_api_utility(api_name, action.get('arguments', {}))
    
    api_name = passed_data.get('api_name')
    api_name = api_name + "_invoke" if api_name else None
    if not api_name:
        return jsonify({
            'status': 'error',
            'message': 'API name is required'
        }), 400

    
    arguments = passed_data.get('parameters', {})
    argument_float_fields = passed_data.get('argument_float_fields', [])  # Get float fields from frontend
    cleaned_arguments = (arguments)
    arguments = cleaned_arguments
    
    # Convert integers to floats based on argument_float_fields
    if argument_float_fields:
        # print(f"Float fields to apply: {argument_float_fields}")
        # print(f"Arguments BEFORE float conversion: {arguments}")
        arguments = apply_float_fields(arguments, argument_float_fields)
        # print(f"Arguments AFTER float conversion: {arguments}")
    
    
    # tools_instance = create_tools_class(session.get("imports_set", []), session.get("invoke_methods", []))
    # if hasattr(tools_instance, api_name):
    try:
        result = execute_api_utility(api_name, arguments)
        # print(g.data)
        # Dynamically call the method with the provided arguments
        # print("Executing API:", api_name, "with arguments:", arguments)
        # result = getattr(tools_instance, api_name)(data=g.data, **arguments)
        # print(f"Result from API {api_name}: {result}")
        session["actions"].append({
            'api_name': api_name,
            'arguments': arguments
        })
        parsed_result = json.loads(result) if isinstance(result, str) else result
        float_fields = list(detect_float_fields(parsed_result))
        # parsed_result = convert_floats_to_strings(parsed_result)
        # print("parsed_res:" , (parsed_result))
        # print(type(result))
        return jsonify({'output': parsed_result, 'float_fields': float_fields}), 200
        
        # return jsonify({
        #     'output': json.loads(result) if isinstance(result, str) else result
        # }), 200
    except Exception as e:
        # print(f"Error executing API {api_name}: {str(e)}")
        return_message = str(e)
        if "expected an indented block" in return_message:
            return_message = "Click on GO to reload the session"
        return jsonify({
            'status': 'error',
            'message': f'Failed to execute API: {return_message}'
        }), 500
# else:
#     return jsonify({
#         'status': 'error',
#         'message': f'API {api_name} not found'
#     }), 404