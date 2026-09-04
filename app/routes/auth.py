from datetime import datetime, timezone

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_user, logout_user

from app.extensions import db
from app.forms.auth import LoginForm
from app.models.user import User


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(
            username=form.username.data.strip()
        ).first()

        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash(
                    "Your account is inactive. Please contact the administrator.",
                    "danger"
                )
                return render_template("auth/login.html", form=form)

            user.last_login = datetime.now(timezone.utc)
            db.session.commit()

            login_user(user)

            return redirect(url_for("home"))

        flash("Invalid username or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("auth.login"))
