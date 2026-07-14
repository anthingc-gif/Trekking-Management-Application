from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db, cache
from app.models import User, Trek, Booking
from app.utils.decorators import staff_required

staff_bp = Blueprint('staff', __name__)


@staff_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@staff_required
def dashboard():
    """Get staff dashboard data."""
    current_user_id = int(get_jwt_identity())

    assigned_treks = Trek.query.filter_by(assigned_staff_id=current_user_id).all()
    trek_data = []

    for trek in assigned_treks:
        registered_count = Booking.query.filter_by(trek_id=trek.id, status='Booked').count()
        trek_data.append({
            **trek.to_dict(),
            'registered_users': registered_count
        })

    return jsonify({
        'assigned_treks': trek_data,
        'total_assigned': len(assigned_treks)
    }), 200


@staff_bp.route('/treks', methods=['GET'])
@jwt_required()
@staff_required
def get_assigned_treks():
    """Get treks assigned to this staff member."""
    current_user_id = int(get_jwt_identity())
    treks = Trek.query.filter_by(assigned_staff_id=current_user_id).order_by(Trek.start_date.desc()).all()

    trek_data = []
    for trek in treks:
        registered_count = Booking.query.filter_by(trek_id=trek.id, status='Booked').count()
        trek_data.append({
            **trek.to_dict(),
            'registered_users': registered_count
        })

    return jsonify({'treks': trek_data}), 200


@staff_bp.route('/treks/<int:trek_id>', methods=['PUT'])
@jwt_required()
@staff_required
def update_trek(trek_id):
    """Update trek details (slots, status) by assigned staff."""
    current_user_id = int(get_jwt_identity())
    trek = Trek.query.get_or_404(trek_id)

    # Ensure staff is assigned to this trek
    if trek.assigned_staff_id != current_user_id:
        return jsonify({'error': 'You are not assigned to this trek'}), 403

    data = request.get_json()

    if 'available_slots' in data:
        new_slots = int(data['available_slots'])
        if new_slots < 0:
            return jsonify({'error': 'Available slots cannot be negative'}), 400
        if new_slots > trek.total_slots:
            return jsonify({'error': f'Available slots cannot exceed total slots ({trek.total_slots})'}), 400
        trek.available_slots = new_slots

    if 'status' in data:
        allowed_statuses = ['Open', 'Closed', 'Completed']
        if data['status'] not in allowed_statuses:
            return jsonify({'error': f'Status must be one of: {", ".join(allowed_statuses)}'}), 400
        trek.status = data['status']

        # If trek is completed, mark all bookings as completed
        if data['status'] == 'Completed':
            bookings = Booking.query.filter_by(trek_id=trek_id, status='Booked').all()
            for booking in bookings:
                booking.status = 'Completed'

    db.session.commit()
    cache.delete('treks_open')

    return jsonify({'message': 'Trek updated successfully', 'trek': trek.to_dict()}), 200


@staff_bp.route('/treks/<int:trek_id>/participants', methods=['GET'])
@jwt_required()
@staff_required
def get_participants(trek_id):
    """Get list of registered participants for a trek."""
    current_user_id = int(get_jwt_identity())
    trek = Trek.query.get_or_404(trek_id)

    # Ensure staff is assigned to this trek
    if trek.assigned_staff_id != current_user_id:
        return jsonify({'error': 'You are not assigned to this trek'}), 403

    bookings = Booking.query.filter_by(trek_id=trek_id).all()
    participants = []

    for booking in bookings:
        participants.append({
            'booking_id': booking.id,
            'user_id': booking.user_id,
            'user_name': booking.user.name,
            'user_email': booking.user.email,
            'user_phone': booking.user.phone,
            'booking_date': booking.booking_date.isoformat() if booking.booking_date else None,
            'status': booking.status,
            'payment_status': booking.payment_status
        })

    return jsonify({
        'trek': trek.to_dict(),
        'participants': participants,
        'total_participants': len([p for p in participants if p['status'] == 'Booked'])
    }), 200
