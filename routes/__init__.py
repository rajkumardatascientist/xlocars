# routes/__init__.py
from .auth import auth_bp
from .cars import cars_bp
from .admin import admin_bp
from .payments import payments_bp
from .about import about_bp
from .dashboard import dashboard_bp

# That's it.  No other imports unless you have other route blueprints.