from datetime import datetime, timezone

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_user, logout_user

from app.extensions import db
from app.forms.auth import LoginForm
from app.forms.invitation_registration import InvitationRegistrationForm
from app.models.family_member import FamilyMember
from app.models.invitation import Invitation
from app.models.user import User


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("admin.dashboard"))

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

                return render_template(
                    "auth/login.html",
                    form=form
                )

            if user.role == "member":
                linked_member = FamilyMember.query.filter_by(
                    user_id=user.id
                ).first()

                if not linked_member:
                    flash(
                        "Your account is not linked to a family member profile. "
                        "Please contact the administrator.",
                        "danger"
                    )

                    return render_template(
                        "auth/login.html",
                        form=form
                    )

            user.last_login = datetime.now(timezone.utc)

            db.session.commit()

            login_user(user)

            if user.role == "admin":
                return redirect(
                    url_for("admin.dashboard")
                )

            return redirect(
                url_for("home")
            )

        flash(
            "Invalid username or password.",
            "danger"
        )

    return render_template(
        "auth/login.html",
        form=form
    )


@auth_bp.route(
    "/register/invite/<token>",
    methods=["GET", "POST"]
)
def register_invitation(token):
    if current_user.is_authenticated:
        return redirect(
            url_for("home")
        )

    invitation = Invitation.query.filter_by(
        token=token
    ).first()

    if not invitation:
        return render_template(
            "auth/invitation_invalid.html",
            reason="This invitation link does not exist."
        ), 404

    if invitation.used_at is not None:
        return render_template(
            "auth/invitation_invalid.html",
            reason="This invitation has already been used."
        ), 400

    if invitation.revoked_at is not None:
        return render_template(
            "auth/invitation_invalid.html",
            reason="This invitation has been revoked by the administrator."
        ), 400

    if not invitation.is_valid():
        return render_template(
            "auth/invitation_invalid.html",
            reason="This invitation has expired."
        ), 400

    member = invitation.member

    if member.user_id is not None:
        return render_template(
            "auth/invitation_invalid.html",
            reason="This family member already has a login account."
        ), 400

    form = InvitationRegistrationForm()

    if member.email and not form.email.data:
        form.email.data = member.email

    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()

        existing_username = User.query.filter_by(
            username=username
        ).first()

        if existing_username:
            flash(
                "That username is already in use.",
                "danger"
            )

            return render_template(
                "auth/invitation_register.html",
                invitation=invitation,
                member=member,
                form=form
            )

        existing_email = User.query.filter_by(
            email=email
        ).first()

        if existing_email:
            flash(
                "That email address is already in use.",
                "danger"
            )

            return render_template(
                "auth/invitation_register.html",
                invitation=invitation,
                member=member,
                form=form
            )

        if member.user_id is not None:
            flash(
                "This family member already has a login account.",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        user = User(
            username=username,
            email=email,
            role="member",
            is_active=True
        )

        user.set_password(
            form.password.data
        )

        db.session.add(user)
        db.session.flush()

        member.user_id = user.id

        invitation.used_at = datetime.now(
            timezone.utc
        )

        db.session.commit()

        flash(
            "Your account was created successfully. You can now log in.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "auth/invitation_register.html",
        invitation=invitation,
        member=member,
        form=form
    )


@auth_bp.route("/logout")
def logout():
    logout_user()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )