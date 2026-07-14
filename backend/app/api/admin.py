from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db, cache
from app.models import User, Trek, Booking
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@admin_required
def dashboard():
    """Get admin dashboard statistics."""
    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role='trekker').count()
    total_staff = User.query.filter_by(role='staff').count()
    total_bookings = Booking.query.count()
    active_treks = Trek.query.filter(Trek.status.in_(['Open', 'Approved'])).count()
    completed_treks = Trek.query.filter_by(status='Completed').count()

    return jsonify({
        'total_treks': total_treks,
        'total_users': total_users,
        'total_staff': total_staff,
        'total_bookings': total_bookings,
        'active_treks': active_treks,
        'completed_treks': completed_treks
    }), 200


# --- Trek Management ---

@admin_bp.route('/treks', methods=['GET'])
@jwt_required()
@admin_required
def get_all_treks():
    """Get all treks."""
    treks = Trek.query.order_by(Trek.created_at.desc()).all()
    return jsonify({'treks': [trek.to_dict() for trek in treks]}), 200


@admin_bp.route('/treks', methods=['POST'])
@jwt_required()
@admin_required
def create_trek():
    """Create a new trek."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required_fields = ['name', 'location', 'difficulty', 'duration_days', 'total_slots', 'start_date', 'end_date']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'{field} is required'}), 400

    # Validate difficulty
    if data['difficulty'] not in ['Easy', 'Moderate', 'Hard']:
        return jsonify({'error': 'Difficulty must be Easy, Moderate, or Hard'}), 400

    from datetime import datetime
    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    if end_date <= start_date:
        return jsonify({'error': 'End date must be after start date'}), 400

    trek = Trek(
        name=data['name'],
        location=data['location'],
        difficulty=data['difficulty'],
        duration_days=int(data['duration_days']),
        total_slots=int(data['total_slots']),
        available_slots=int(data['total_slots']),
        status=data.get('status', 'Pending'),
        start_date=start_date,
        end_date=end_date,
        description=data.get('description', ''),
        price=float(data.get('price', 0))
    )

    db.session.add(trek)
    db.session.commit()

    # Invalidate cache
    cache.delete('treks_open')

    return jsonify({'message': 'Trek created successfully', 'trek': trek.to_dict()}), 201


@admin_bp.route('/treks/<int:trek_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_trek(trek_id):
    """Update a trek."""
    trek = Trek.query.get_or_404(trek_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    from datetime import datetime

    if 'name' in data:
        trek.name = data['name']
    if 'location' in data:
        trek.location = data['location']
    if 'difficulty' in data:
        if data['difficulty'] not in ['Easy', 'Moderate', 'Hard']:
            return jsonify({'error': 'Difficulty must be Easy, Moderate, or Hard'}), 400
        trek.difficulty = data['difficulty']
    if 'duration_days' in data:
        trek.duration_days = int(data['duration_days'])
    if 'total_slots' in data:
        booked = trek.total_slots - trek.available_slots
        new_total = int(data['total_slots'])
        if new_total < booked:
            return jsonify({'error': f'Cannot reduce slots below {booked} (already booked)'}), 400
        trek.available_slots = new_total - booked
        trek.total_slots = new_total
    if 'status' in data:
        trek.status = data['status']
    if 'start_date' in data:
        trek.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    if 'end_date' in data:
        trek.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    if 'description' in data:
        trek.description = data['description']
    if 'price' in data:
        trek.price = float(data['price'])

    db.session.commit()
    cache.delete('treks_open')

    return jsonify({'message': 'Trek updated successfully', 'trek': trek.to_dict()}), 200


@admin_bp.route('/treks/<int:trek_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_trek(trek_id):
    """Delete a trek."""
    trek = Trek.query.get_or_404(trek_id)

    # Check if there are active bookings
    active_bookings = Booking.query.filter_by(trek_id=trek_id, status='Booked').count()
    if active_bookings > 0:
        return jsonify({'error': f'Cannot delete trek with {active_bookings} active bookings'}), 400

    db.session.delete(trek)
    db.session.commit()
    cache.delete('treks_open')

    return jsonify({'message': 'Trek deleted successfully'}), 200


@admin_bp.route('/treks/<int:trek_id>/assign', methods=['PUT'])
@jwt_required()
@admin_required
def assign_staff_to_trek(trek_id):
    """Assign a staff member to a trek."""
    trek = Trek.query.get_or_404(trek_id)
    data = request.get_json()

    staff_id = data.get('staff_id')
    if not staff_id:
        return jsonify({'error': 'staff_id is required'}), 400

    staff = User.query.get(staff_id)
    if not staff or staff.role != 'staff':
        return jsonify({'error': 'Invalid staff member'}), 404

    if not staff.is_active:
        return jsonify({'error': 'Staff member is deactivated'}), 400

    trek.assigned_staff_id = staff_id
    db.session.commit()

    return jsonify({'message': f'Staff {staff.name} assigned to trek {trek.name}', 'trek': trek.to_dict()}), 200


# --- Staff Management ---

@admin_bp.route('/staff', methods=['GET'])
@jwt_required()
@admin_required
def get_all_staff():
    """Get all staff members."""
    staff_list = User.query.filter_by(role='staff').order_by(User.created_at.desc()).all()
    return jsonify({'staff': [s.to_dict() for s in staff_list]}), 200


@admin_bp.route('/staff', methods=['POST'])
@jwt_required()
@admin_required
def create_staff():
    """Create a new staff member."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()

    if not email or not password or not name:
        return jsonify({'error': 'Email, password, and name are required'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    staff = User(
        email=email,
        name=name,
        phone=phone,
        role='staff',
        is_active=True
    )
    staff.set_password(password)

    db.session.add(staff)
    db.session.commit()

    return jsonify({'message': 'Staff member created successfully', 'staff': staff.to_dict()}), 201


@admin_bp.route('/staff/<int:staff_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_staff(staff_id):
    """Update staff member details."""
    staff = User.query.get_or_404(staff_id)

    if staff.role != 'staff':
        return jsonify({'error': 'User is not a staff member'}), 400

    data = request.get_json()

    if 'name' in data:
        staff.name = data['name']
    if 'phone' in data:
        staff.phone = data['phone']
    if 'email' in data:
        existing = User.query.filter_by(email=data['email'].lower()).first()
        if existing and existing.id != staff_id:
            return jsonify({'error': 'Email already in use'}), 409
        staff.email = data['email'].lower()
    if 'password' in data and data['password']:
        staff.set_password(data['password'])

    db.session.commit()

    return jsonify({'message': 'Staff updated successfully', 'staff': staff.to_dict()}), 200


@admin_bp.route('/staff/<int:staff_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_staff(staff_id):
    """Deactivate a staff member."""
    staff = User.query.get_or_404(staff_id)

    if staff.role != 'staff':
        return jsonify({'error': 'User is not a staff member'}), 400

    staff.is_active = False
    db.session.commit()

    return jsonify({'message': 'Staff member deactivated'}), 200


# --- User Management ---

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users():
    """Get all trekker users."""
    users = User.query.filter_by(role='trekker').order_by(User.created_at.desc()).all()
    return jsonify({'users': [u.to_dict() for u in users]}), 200


@admin_bp.route('/users/<int:user_id>/blacklist', methods=['PUT'])
@jwt_required()
@admin_required
def toggle_blacklist(user_id):
    """Toggle blacklist status for a user or staff."""
    user = User.query.get_or_404(user_id)

    if user.role == 'admin':
        return jsonify({'error': 'Cannot blacklist admin'}), 400

    user.is_blacklisted = not user.is_blacklisted
    db.session.commit()

    status = 'blacklisted' if user.is_blacklisted else 'unblacklisted'
    return jsonify({'message': f'User {status} successfully', 'user': user.to_dict()}), 200


@admin_bp.route('/users/<int:user_id>/deactivate', methods=['PUT'])
@jwt_required()
@admin_required
def toggle_deactivate(user_id):
    """Toggle active status for a user or staff."""
    user = User.query.get_or_404(user_id)

    if user.role == 'admin':
        return jsonify({'error': 'Cannot deactivate admin'}), 400

    user.is_active = not user.is_active
    db.session.commit()

    status = 'activated' if user.is_active else 'deactivated'
    return jsonify({'message': f'User {status} successfully', 'user': user.to_dict()}), 200


# --- Bookings ---

@admin_bp.route('/bookings', methods=['GET'])
@jwt_required()
@admin_required
def get_all_bookings():
    """Get all bookings."""
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return jsonify({'bookings': [b.to_dict() for b in bookings]}), 200


# --- Search ---

@admin_bp.route('/search', methods=['GET'])
@jwt_required()
@admin_required
def search():
    """Search users, staff, and treks."""
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')  # all, users, staff, treks

    if not query:
        return jsonify({'error': 'Search query is required'}), 400

    results = {}
    search_term = f'%{query}%'

    if search_type in ('all', 'users'):
        users = User.query.filter(
            User.role == 'trekker',
            (User.name.ilike(search_term) | User.email.ilike(search_term))
        ).all()
        results['users'] = [u.to_dict() for u in users]

    if search_type in ('all', 'staff'):
        staff = User.query.filter(
            User.role == 'staff',
            (User.name.ilike(search_term) | User.email.ilike(search_term))
        ).all()
        results['staff'] = [s.to_dict() for s in staff]

    if search_type in ('all', 'treks'):
        treks = Trek.query.filter(
            (Trek.name.ilike(search_term) | Trek.location.ilike(search_term))
        ).all()
        results['treks'] = [t.to_dict() for t in treks]

    return jsonify(results), 200
