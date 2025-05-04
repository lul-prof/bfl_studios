from flask import Blueprint

# Import all route blueprints
from .auth import bp as auth_bp
from .booking import bp as booking_bp
from .admin import bp as admin_bp
from .user import bp as user_bp
from .main import bp as main_bp
from .payment import bp as payment_bp

# These blueprints are imported in app/__init__.py