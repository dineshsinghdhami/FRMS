from flask import Flask, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, logout_user

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
    from app.models.announcement import Announcement
    from app.models.gallery_photo import GalleryPhoto
    from app.models.document import Document
    from app.models.family_history import FamilyHistory

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(
            User,
            int(user_id)
        )

    @app.before_request
    def check_user_access():
        if not current_user.is_authenticated:
            return None

        if not current_user.is_active:
            logout_user()

            flash(
                "Your account has been disabled. Please contact the administrator.",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        if current_user.role == "member":
            linked_member = FamilyMember.query.filter_by(
                user_id=current_user.id
            ).first()

            if not linked_member:
                logout_user()

                flash(
                    "Your account is no longer linked to a family member profile. "
                    "Please contact the administrator.",
                    "danger"
                )

                return redirect(
                    url_for("auth.login")
                )

        return None

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

    from app.routes.family_history import family_history_bp
    app.register_blueprint(family_history_bp)

    from app.routes.admin_documents import admin_documents_bp
    app.register_blueprint(admin_documents_bp)

    from app.routes.admin_family_history import admin_family_history_bp
    app.register_blueprint(admin_family_history_bp)

    from app.routes.admin_users import admin_users_bp
    app.register_blueprint(admin_users_bp)

    @app.errorhandler(413)
    def file_too_large(error):
        return render_template(
            "errors/413.html"
        ), 413

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