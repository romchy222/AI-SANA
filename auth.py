from flask import Blueprint, request, jsonify, session
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/verify-session', methods=['GET'])
def verify_session():
    """Verify admin session"""
    try:
        from models import AdminUser
        
        admin_id = session.get('admin_id')
        if admin_id:
            admin = AdminUser.query.filter_by(id=admin_id, is_active=True).first()
            if admin:
                return jsonify({'authenticated': True, 'username': admin.username})
        
        return jsonify({'authenticated': False})
    except Exception as e:
        logger.error(f"Error verifying session: {str(e)}")
        return jsonify({'authenticated': False})
