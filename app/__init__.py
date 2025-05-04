from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from .config import Config
from datetime import datetime

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()

# Add the user loader callback
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
    
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.context_processor
    def utility_processor():
        return {
            'current_year': datetime.now().year
        } 

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Register blueprints
    from .routes import auth, booking, admin, user,main,payment
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(booking.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(payment.bp)
    app.register_blueprint(user.bp)

    return app