from celery import Celery
from celery.schedules import crontab


def make_celery(app=None):
    """Create Celery instance configured for TMA."""
    celery = Celery(
        'tma',
        broker='redis://localhost:6379/1',
        backend='redis://localhost:6379/1'
    )

    if app:
        celery.conf.update(app.config)

    # Task discovery
    celery.conf.task_routes = {
        'send_daily_reminders': {'queue': 'default'},
        'generate_monthly_report': {'queue': 'default'},
        'export_booking_history': {'queue': 'default'}
    }

    # Celery Beat schedule
    celery.conf.beat_schedule = {
        'daily-reminders': {
            'task': 'send_daily_reminders',
            'schedule': crontab(hour=8, minute=0),  # Every day at 8 AM
        },
        'monthly-report': {
            'task': 'generate_monthly_report',
            'schedule': crontab(day_of_month=1, hour=9, minute=0),  # 1st of every month
        }
    }

    celery.conf.timezone = 'UTC'

    return celery


# Create celery instance for worker
celery_app = make_celery()


# Register tasks
@celery_app.task(name='send_daily_reminders')
def send_daily_reminders():
    """Send daily reminders for upcoming treks."""
    from app import create_app
    app = create_app()
    with app.app_context():
        from app.tasks.reminders import send_daily_reminders_sync
        return send_daily_reminders_sync()


@celery_app.task(name='generate_monthly_report')
def generate_monthly_report():
    """Generate monthly activity report."""
    from app import create_app
    app = create_app()
    with app.app_context():
        from app.tasks.reports import generate_monthly_report_sync
        return generate_monthly_report_sync()


@celery_app.task(name='export_booking_history')
def export_booking_history(user_id):
    """Export booking history as CSV for a user."""
    from app import create_app
    app = create_app()
    with app.app_context():
        from app.tasks.exports import export_booking_history_sync
        return export_booking_history_sync(user_id)
