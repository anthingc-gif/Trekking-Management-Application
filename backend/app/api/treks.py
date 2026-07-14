from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import cache
from app.models import Trek

treks_bp = Blueprint('treks', __name__)


@treks_bp.route('', methods=['GET'])
@jwt_required()
def get_open_treks():
    """Get all open/approved treks available for booking."""
    # Try cache first
    cached = cache.get('treks_open')
    if cached:
        return jsonify({'treks': cached}), 200

    treks = Trek.query.filter(Trek.status.in_(['Open', 'Approved'])).order_by(Trek.start_date.asc()).all()
    treks_data = [trek.to_dict() for trek in treks]

    # Cache for 5 minutes
    cache.set('treks_open', treks_data, timeout=300)

    return jsonify({'treks': treks_data}), 200


@treks_bp.route('/<int:trek_id>', methods=['GET'])
@jwt_required()
def get_trek_detail(trek_id):
    """Get single trek details."""
    trek = Trek.query.get_or_404(trek_id)
    return jsonify({'trek': trek.to_dict()}), 200


@treks_bp.route('/search', methods=['GET'])
@jwt_required()
def search_treks():
    """Search and filter treks."""
    query = request.args.get('q', '').strip()
    difficulty = request.args.get('difficulty', '').strip()
    location = request.args.get('location', '').strip()
    min_duration = request.args.get('min_duration', type=int)
    max_duration = request.args.get('max_duration', type=int)
    status = request.args.get('status', '').strip()

    treks_query = Trek.query

    # Only show open treks to users unless status specified
    if status:
        treks_query = treks_query.filter_by(status=status)
    else:
        treks_query = treks_query.filter(Trek.status.in_(['Open', 'Approved']))

    if query:
        search_term = f'%{query}%'
        treks_query = treks_query.filter(
            (Trek.name.ilike(search_term) | Trek.location.ilike(search_term))
        )

    if difficulty:
        treks_query = treks_query.filter_by(difficulty=difficulty)

    if location:
        treks_query = treks_query.filter(Trek.location.ilike(f'%{location}%'))

    if min_duration:
        treks_query = treks_query.filter(Trek.duration_days >= min_duration)

    if max_duration:
        treks_query = treks_query.filter(Trek.duration_days <= max_duration)

    treks = treks_query.order_by(Trek.start_date.asc()).all()

    return jsonify({'treks': [trek.to_dict() for trek in treks]}), 200
