from flask import Blueprint, render_template, request

trajectory_viewer_bp = Blueprint('trajectory_viewer', __name__)


@trajectory_viewer_bp.route('/trajectory_viewer', strict_slashes=False, methods=['GET'])
def trajectory_viewer():
    return render_template('trajectory_viewer.html')