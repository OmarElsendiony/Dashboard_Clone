from flask import Blueprint, render_template, request

health_bp = Blueprint('health', __name__)



####################### Deployment Health Check Endpoint #######################
@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for load balancers and monitoring"""
    try:
        # Check Redis connection
        redis_client = app.config.get('SESSION_REDIS')
        if redis_client:
            redis_client.ping()
        
        return {
            'status': 'healthy',
            'timestamp': str(datetime.now()),
            'services': {
                'redis': 'connected' if redis_client else 'not_configured'
            }
        }, 200
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': str(datetime.now())
        }, 503
