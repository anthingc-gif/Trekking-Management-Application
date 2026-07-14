from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models import User


def role_required(*roles):
    """Decorator to restrict access based on user role."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user_id = int(get_jwt_identity())
            user = User.query.get(current_user_id)

            if not user:
                return jsonify({'error': 'User not found'}), 404

            if not user.is_active:
                return jsonify({'error': 'Account is deactivated'}), 403

            if user.is_blacklisted:
                return jsonify({'error': 'Account is blacklisted'}), 403

            if user.role not in roles:
                return jsonify({'error': 'Access denied. Insufficient permissions.'}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    """Decorator to restrict access to admin only."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        return fn(*args, **kwargs)
    return wrapper


def staff_required(fn):
    """Decorator to restrict access to staff only."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or user.role != 'staff':
            return jsonify({'error': 'Staff access required'}), 403

        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403

        return fn(*args, **kwargs)
    return wrapper
