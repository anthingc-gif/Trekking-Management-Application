import csv
import os
from datetime import datetime


def export_booking_history_sync(user_id):
    """Synchronous export fallback when Celery is not running."""
    from app.models import Booking, Notification
    from app.extensions import db
    from flask import current_app

    export_dir = current_app.config.get('EXPORT_DIR', 'exports')
    os.makedirs(export_dir, exist_ok=True)

    bookings = Booking.query.filter_by(user_id=user_id).all()

    filename = f'booking_history_{user_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    filepath = os.path.join(export_dir, filename)

    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['User ID', 'Trek Name', 'Location', 'Booking Status', 'Booking Date', 'Start Date', 'End Date'])

        for booking in bookings:
            writer.writerow([
                booking.user_id,
                booking.trek.name if booking.trek else 'N/A',
                booking.trek.location if booking.trek else 'N/A',
                booking.status,
                booking.booking_date.strftime('%Y-%m-%d') if booking.booking_date else 'N/A',
                booking.trek.start_date.isoformat() if booking.trek and booking.trek.start_date else 'N/A',
                booking.trek.end_date.isoformat() if booking.trek and booking.trek.end_date else 'N/A'
            ])

    # Create notification
    notification = Notification(
        user_id=user_id,
        message=f'Your booking history export is ready: {filename}',
        type='success'
    )
    db.session.add(notification)
    db.session.commit()

    return filename


def make_celery_export_task(celery_app):
    """Create Celery task for async export."""

    @celery_app.task(name='export_booking_history')
    def export_booking_history(user_id):
        """Async Celery task to export booking history."""
        from app import create_app
        app = create_app()
        with app.app_context():
            return export_booking_history_sync(user_id)

    return export_booking_history
