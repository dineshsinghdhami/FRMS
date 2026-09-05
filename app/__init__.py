from flask import Flask, redirect, url_for
from flask_login import current_user, login_required

from config import Config
from app.extensions import csrf, db, login_manager, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    from app.models.user import User
    from app.models.family_member import FamilyMember
    from app.models.relationship import Relationship
    from app.models.timeline_event import TimelineEvent
    from app.models.activity import Activity
    from app.models.event import Event

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(
            User,
            int(user_id)
        )

    migrate.init_app(
        app,
        db
    )

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    from app.routes.timeline import timeline_bp
    app.register_blueprint(timeline_bp)

    from app.routes.member import member_bp
    app.register_blueprint(member_bp)

    @app.route("/")
    @login_required
    def home():
        if current_user.role == "admin":
            return redirect(
                url_for("admin.dashboard")
            )

        if current_user.role == "member":
            return redirect(
                url_for("member.dashboard")
            )

        return """
        <h2>Family Record Management System</h2>
        <p>You are logged in successfully.</p>
        <a href="/logout">Logout</a>
        """

    return app