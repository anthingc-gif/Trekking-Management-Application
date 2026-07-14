from datetime import datetime, timedelta


def generate_monthly_report_sync():
    """Generate monthly activity report for admin."""
    from app.models import Trek, Booking, User, Notification
    from app.extensions import db

    # Get data for the previous month
    today = datetime.utcnow().date()
    first_of_month = today.replace(day=1)
    last_month_end = first_of_month - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    # Treks conducted last month
    treks_conducted = Trek.query.filter(
        Trek.start_date >= last_month_start,
        Trek.start_date <= last_month_end,
        Trek.status == 'Completed'
    ).count()

    # Users who participated
    bookings_last_month = Booking.query.filter(
        Booking.booking_date >= datetime.combine(last_month_start, datetime.min.time()),
        Booking.booking_date <= datetime.combine(last_month_end, datetime.max.time()),
        Booking.status.in_(['Booked', 'Completed'])
    ).count()

    # Most popular treks (by bookings)
    from sqlalchemy import func
    popular_treks = db.session.query(
        Trek.name,
        func.count(Booking.id).label('booking_count')
    ).join(Booking).filter(
        Booking.booking_date >= datetime.combine(last_month_start, datetime.min.time()),
        Booking.booking_date <= datetime.combine(last_month_end, datetime.max.time())
    ).group_by(Trek.name).order_by(func.count(Booking.id).desc()).limit(5).all()

    # Total new users last month
    new_users = User.query.filter(
        User.created_at >= datetime.combine(last_month_start, datetime.min.time()),
        User.created_at <= datetime.combine(last_month_end, datetime.max.time()),
        User.role == 'trekker'
    ).count()

    # Build HTML report
    report_html = f"""
    <html>
    <head><style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        h1 {{ color: #2c3e50; }}
        .stat {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; }}
        .stat h3 {{ margin: 0; color: #495057; }}
        .stat p {{ margin: 5px 0 0; font-size: 24px; font-weight: bold; color: #2c3e50; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #dee2e6; }}
        th {{ background: #e9ecef; }}
    </style></head>
    <body>
        <h1>Monthly Trekking Activity Report</h1>
        <p>Report Period: {last_month_start.strftime('%B %d')} - {last_month_end.strftime('%B %d, %Y')}</p>

        <div class="stat">
            <h3>Treks Conducted</h3>
            <p>{treks_conducted}</p>
        </div>

        <div class="stat">
            <h3>Total Bookings</h3>
            <p>{bookings_last_month}</p>
        </div>

        <div class="stat">
            <h3>New Users Registered</h3>
            <p>{new_users}</p>
        </div>

        <h2>Popular Treks</h2>
        <table>
            <tr><th>Trek Name</th><th>Bookings</th></tr>
            {''.join(f'<tr><td>{name}</td><td>{count}</td></tr>' for name, count in popular_treks) if popular_treks else '<tr><td colspan="2">No data available</td></tr>'}
        </table>

        <p style="margin-top: 30px; color: #6c757d; font-size: 12px;">
            Generated on {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')} | Trekking Management Application
        </p>
    </body>
    </html>
    """

    # Create notification for admin
    admin = User.query.filter_by(role='admin').first()
    if admin:
        notification = Notification(
            user_id=admin.id,
            message=f'Monthly activity report for {last_month_start.strftime("%B %Y")} has been generated.',
            type='info'
        )
        db.session.add(notification)
        db.session.commit()

    return report_html


def make_celery_report_task(celery_app):
    """Create Celery task for monthly reports."""

    @celery_app.task(name='generate_monthly_report')
    def generate_monthly_report():
        from app import create_app
        app = create_app()
        with app.app_context():
            return generate_monthly_report_sync()

    return generate_monthly_report
