from datetime import datetime, timedelta


def send_daily_reminders_sync():
    """Send daily reminders for upcoming treks."""
    from app.models import Booking, Trek, Notification, User
    from app.extensions import db

    # Find treks starting within the next 3 days
    today = datetime.utcnow().date()
    upcoming_date = today + timedelta(days=3)

    upcoming_treks = Trek.query.filter(
        Trek.start_date >= today,
        Trek.start_date <= upcoming_date,
        Trek.status.in_(['Open', 'Approved'])
    ).all()

    reminders_sent = 0

    for trek in upcoming_treks:
        # Get all booked users for this trek
        bookings = Booking.query.filter_by(trek_id=trek.id, status='Booked').all()

        for booking in bookings:
            days_until = (trek.start_date - today).days
            message = (
                f'Reminder: Your trek "{trek.name}" at {trek.location} '
                f'starts in {days_until} day(s) on {trek.start_date.strftime("%B %d, %Y")}. '
                f'Get ready for the adventure!'
            )

            notification = Notification(
                user_id=booking.user_id,
                message=message,
                type='info'
            )
            db.session.add(notification)
            reminders_sent += 1

    db.session.commit()
    return f'{reminders_sent} reminders sent for {len(upcoming_treks)} upcoming treks'


def make_celery_reminder_task(celery_app):
    """Create Celery task for daily reminders."""

    @celery_app.task(name='send_daily_reminders')
    def send_daily_reminders():
        from app import create_app
        app = create_app()
        with app.app_context():
            return send_daily_reminders_sync()

    return send_daily_reminders
