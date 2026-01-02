import os
from flask import Blueprint, render_template, request, jsonify
from openai import OpenAI

sop_validator_bp = Blueprint('sop_validator', __name__)


@sop_validator_bp.route('/sop_validator', strict_slashes=False, methods=["GET", "POST"])
def sop_validator():
    if request.method == "POST":
        data = request.json
        action = data.get('action')
        
        if not action:
            return jsonify({
                'status': 'error',
                'message': 'Action is required'
            }), 400
        
        if action == "validate_sop":
            sop = data.get('sop', '')
            data_flow = data.get('data_flow', '')
            
            if not sop or not data_flow:
                return jsonify({
                    'status': 'error',
                    'message': 'Both SOP and Data Flow are required'
                }), 400
            
            # Load the validation prompt
            validation_prompt_path = "prompts/sop_validator/validation_prompt.txt"
            
            if not os.path.exists(validation_prompt_path):
                return jsonify({
                    'status': 'error',
                    'message': 'Validation prompt file not found'
                }), 404
            
            with open(validation_prompt_path, 'r') as file:
                validation_prompt = file.read()
            
            # Format the prompt with the provided SOP and data flow
            prompt = validation_prompt.format(
                sop=sop,
                data_flow=data_flow
            )
            
            # Call OpenAI API
            try:
                client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an expert at validating Standard Operating Procedures (SOPs) and their data flows. You ensure logical consistency, proper argument sourcing, and identify any issues with data flow."},
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
                    'message': f'Failed to validate SOP: {str(e)}'
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid action'
            }), 400
    
    return render_template('sop_validator.html')
