from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User, Notification

users_bp = Blueprint('users', __name__)


@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get_or_404(current_user_id)
    return jsonify({'user': user.to_dict()}), 200


@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get_or_404(current_user_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'name' in data and data['name'].strip():
        user.name = data['name'].strip()
    if 'phone' in data:
        user.phone = data['phone'].strip()
    if 'email' in data and data['email'].strip():
        email = data['email'].strip().lower()
        existing = User.query.filter_by(email=email).first()
        if existing and existing.id != current_user_id:
            return jsonify({'error': 'Email already in use'}), 409
        user.email = email
    if 'password' in data and data['password']:
        if len(data['password']) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        user.set_password(data['password'])

    db.session.commit()

    return jsonify({'message': 'Profile updated successfully', 'user': user.to_dict()}), 200


@users_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get user notifications."""
    current_user_id = int(get_jwt_identity())
    notifications = Notification.query.filter_by(user_id=current_user_id).order_by(
        Notification.created_at.desc()
    ).limit(20).all()

    return jsonify({'notifications': [n.to_dict() for n in notifications]}), 200


@users_bp.route('/notifications/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark a notification as read."""
    current_user_id = int(get_jwt_identity())
    notification = Notification.query.get_or_404(notification_id)

    if notification.user_id != current_user_id:
        return jsonify({'error': 'Access denied'}), 403

    notification.is_read = True
    db.session.commit()

    return jsonify({'message': 'Notification marked as read'}), 200


@users_bp.route('/notifications/read-all', methods=['PUT'])
@jwt_required()
def mark_all_notifications_read():
    """Mark all notifications as read."""
    current_user_id = int(get_jwt_identity())
    Notification.query.filter_by(user_id=current_user_id, is_read=False).update({'is_read': True})
    db.session.commit()

    return jsonify({'message': 'All notifications marked as read'}), 200


@users_bp.route('/export', methods=['POST'])
@jwt_required()
def trigger_export():
    """Trigger CSV export of booking history (async via Celery)."""
    current_user_id = int(get_jwt_identity())

    try:
        from app.tasks.exports import export_booking_history
        task = export_booking_history.delay(current_user_id)

        # Create notification
        notification = Notification(
            user_id=current_user_id,
            message='Your booking history export has been started. You will be notified when ready.',
            type='info'
        )
        db.session.add(notification)
        db.session.commit()

        return jsonify({
            'message': 'Export started. You will be notified when ready.',
            'task_id': task.id
        }), 202
    except Exception as e:
        # Fallback: synchronous export if Celery is not running
        from app.tasks.exports import export_booking_history_sync
        filename = export_booking_history_sync(current_user_id)
        return jsonify({
            'message': 'Export completed',
            'filename': filename
        }), 200
