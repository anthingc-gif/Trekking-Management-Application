from app.extensions import db
from app.models import User


def seed_admin():
    """Create the default admin user programmatically."""
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            email='admin@tma.com',
            name='Admin',
            role='admin',
            is_active=True,
            is_blacklisted=False
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('[SEED] Admin user created: admin@tma.com / admin123')
    else:
        print('[SEED] Admin user already exists.')
