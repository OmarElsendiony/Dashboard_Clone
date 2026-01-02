import os
from flask import Blueprint, render_template, request, jsonify
from openai import OpenAI

tool_schema_extractor_bp = Blueprint('tool_schema_extractor', __name__)


@tool_schema_extractor_bp.route('/tool_schema_extractor', strict_slashes=False, methods=["GET", "POST"])
def tool_schema_extractor():
    if request.method == "POST":
        data = request.json
        action = data.get('action')
        
        if not action:
            return jsonify({
                'status': 'error',
                'message': 'Action is required'
            }), 400
        
        if action == "extract_tool_schemas":
            draft_policy = data.get('draft_policy', '')
            
            if not draft_policy:
                return jsonify({
                    'status': 'error',
                    'message': 'Draft policy content is required'
                }), 400
            
            # Load the extraction prompt
            extraction_prompt_path = "prompts/tool_schema_extractor/extraction_prompt.txt"
            
            if not os.path.exists(extraction_prompt_path):
                return jsonify({
                    'status': 'error',
                    'message': 'Extraction prompt file not found'
                }), 404
            
            with open(extraction_prompt_path, 'r') as file:
                extraction_prompt = file.read()
            
            # Format the prompt with the provided draft policy
            prompt = extraction_prompt.format(
                draft_policy=draft_policy
            )
            
            # Call OpenAI API
            try:
                client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an expert at analyzing function usage patterns across Standard Operating Procedures and extracting correct tool schemas with required/optional argument specifications. You carefully track argument usage percentages and provide clear rationale for each classification."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                
                extraction_result = response.choices[0].message.content.strip()
                
                return jsonify({
                    'status': 'success',
                    'extraction_result': extraction_result
                }), 200
                
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': f'Failed to extract tool schemas: {str(e)}'
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid action'
            }), 400
    
    return render_template('tool_schema_extractor.html')
