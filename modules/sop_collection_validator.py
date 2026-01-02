import os
from flask import Blueprint, render_template, request, jsonify
from openai import OpenAI

sop_collection_validator_bp = Blueprint('sop_collection_validator', __name__)


@sop_collection_validator_bp.route('/sop_collection_validator', strict_slashes=False, methods=["GET", "POST"])
def sop_collection_validator():
    if request.method == "POST":
        data = request.json
        action = data.get('action')
        
        if not action:
            return jsonify({
                'status': 'error',
                'message': 'Action is required'
            }), 400
        
        if action == "validate_sop_collection":
            sops_content = data.get('sops_content', '')
            
            if not sops_content:
                return jsonify({
                    'status': 'error',
                    'message': 'SOPs content is required'
                }), 400
            
            # Load the validation prompt
            validation_prompt_path = "prompts/sop_collection_validator/validation_prompt.txt"
            
            if not os.path.exists(validation_prompt_path):
                return jsonify({
                    'status': 'error',
                    'message': 'Validation prompt file not found'
                }), 404
            
            with open(validation_prompt_path, 'r') as file:
                validation_prompt = file.read()
            
            # Format the prompt with the provided SOPs content
            prompt = validation_prompt.format(
                sops_content=sops_content
            )
            
            # Call OpenAI API
            try:
                client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an expert at validating Standard Operating Procedures (SOPs) for agentic systems. You analyze SOPs for logical coherence, standalone capability, combination compatibility, and instruction formulation readiness."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                
                validation_result = response.choices[0].message.content.strip()
                
                return jsonify({
                    'status': 'success',
                    'validation_result': validation_result
                }), 200
                
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': f'Failed to validate SOP collection: {str(e)}'
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid action'
            }), 400
    
    return render_template('sop_collection_validator.html')
