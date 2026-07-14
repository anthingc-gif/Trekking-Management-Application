from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db, cache
from app.models import User, Trek, Booking, Notification

bookings_bp = Blueprint('bookings', __name__)


@bookings_bp.route('', methods=['POST'])
@jwt_required()
def create_booking():
    """Book a trek."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)

    if user.role != 'trekker':
        return jsonify({'error': 'Only trekkers can book treks'}), 403

    data = request.get_json()
    trek_id = data.get('trek_id')

    if not trek_id:
        return jsonify({'error': 'trek_id is required'}), 400

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    # Business rule: Only Open treks can be booked
    if trek.status != 'Open':
        return jsonify({'error': 'Trek is not open for booking'}), 400

    # Business rule: Prevent overbooking
    if trek.available_slots <= 0:
        return jsonify({'error': 'No available slots for this trek'}), 400

    # Business rule: Prevent duplicate bookings
    existing_booking = Booking.query.filter_by(
        user_id=current_user_id,
        trek_id=trek_id
    ).first()

    if existing_booking:
        if existing_booking.status == 'Booked':
            return jsonify({'error': 'You have already booked this trek'}), 409
        elif existing_booking.status == 'Cancelled':
            # Allow re-booking if previously cancelled
            existing_booking.status = 'Booked'
            existing_booking.payment_status = 'Pending'
            trek.available_slots -= 1
            db.session.commit()
            cache.delete('treks_open')

            # Create notification
            notification = Notification(
                user_id=current_user_id,
                message=f'Your booking for "{trek.name}" has been confirmed.',
                type='success'
            )
            db.session.add(notification)
            db.session.commit()

            return jsonify({'message': 'Trek re-booked successfully', 'booking': existing_booking.to_dict()}), 201

    # Create new booking
    booking = Booking(
        user_id=current_user_id,
        trek_id=trek_id,
        status='Booked',
        payment_status='Pending'
    )

    trek.available_slots -= 1

    db.session.add(booking)

    # Create notification
    notification = Notification(
        user_id=current_user_id,
        message=f'Your booking for "{trek.name}" has been confirmed.',
        type='success'
    )
    db.session.add(notification)
    db.session.commit()
    cache.delete('treks_open')

    return jsonify({'message': 'Trek booked successfully', 'booking': booking.to_dict()}), 201


@bookings_bp.route('', methods=['GET'])
@jwt_required()
def get_my_bookings():
    """Get current user's bookings."""
    current_user_id = int(get_jwt_identity())

    bookings = Booking.query.filter_by(user_id=current_user_id).order_by(Booking.created_at.desc()).all()

    return jsonify({'bookings': [b.to_dict() for b in bookings]}), 200


@bookings_bp.route('/<int:booking_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_booking(booking_id):
    """Cancel a booking."""
    current_user_id = int(get_jwt_identity())
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user_id:
        return jsonify({'error': 'You can only cancel your own bookings'}), 403

    if booking.status != 'Booked':
        return jsonify({'error': 'Only active bookings can be cancelled'}), 400

    booking.status = 'Cancelled'
    booking.payment_status = 'Refunded'

    # Restore available slot
    trek = Trek.query.get(booking.trek_id)
    if trek:
        trek.available_slots += 1

    # Create notification
    notification = Notification(
        user_id=current_user_id,
        message=f'Your booking for "{trek.name}" has been cancelled.',
        type='warning'
    )
    db.session.add(notification)
    db.session.commit()
    cache.delete('treks_open')

    return jsonify({'message': 'Booking cancelled successfully', 'booking': booking.to_dict()}), 200
