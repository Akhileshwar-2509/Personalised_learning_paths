from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    migrate.init_app(app, db)

    from app.routes import main, auth, student, instructor
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(student, url_prefix='/student')
    app.register_blueprint(instructor, url_prefix='/instructor')

    @app.context_processor
    def inject_user_type():
        from flask_login import current_user
        return dict(user_type=current_user.user_type if not current_user.is_anonymous else None)

    return app

from app.models import User, Course, Enrollment, Resource, Assignment

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))