from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.extensions import db
from app.forms.admin_user import AdminResetPasswordForm
from app.forms.create_member_account import CreateMemberAccountForm
from app.forms.link_existing_account import LinkExistingAccountForm
from app.models.activity import Activity
from app.models.announcement import Announcement
from app.models.document import Document
from app.models.event import Event
from app.models.family_history import FamilyHistory
from app.models.family_member import FamilyMember
from app.models.gallery_photo import GalleryPhoto
from app.models.user import User
from app.utilities.decorators import admin_required


admin_users_bp = Blueprint(
    "admin_users",
    __name__,
    url_prefix="/admin/users"
)


@admin_users_bp.route("/")
@login_required
@admin_required
def index():
    users = User.query.order_by(
        User.created_at.desc()
    ).all()

    linked_members = FamilyMember.query.filter(
        FamilyMember.user_id.isnot(None)
    ).all()

    member_map = {
        member.user_id: member
        for member in linked_members
    }

    return render_template(
        "admin/users.html",
        users=users,
        member_map=member_map
    )


@admin_users_bp.route(
    "/<int:user_id>/toggle-status",
    methods=["POST"]
)
@login_required
@admin_required
def toggle_status(user_id):
    user = User.query.get_or_404(user_id)

    if user.role == "admin":
        flash(
            "Admin accounts cannot be disabled from this page.",
            "warning"
        )

        return redirect(
            url_for("admin_users.index")
        )

    user.is_active = not user.is_active

    db.session.commit()

    if user.is_active:
        flash(
            f"{user.username} has been activated successfully.",
            "success"
        )
    else:
        flash(
            f"{user.username} has been disabled successfully.",
            "success"
        )

    return redirect(
        url_for("admin_users.index")
    )


@admin_users_bp.route(
    "/<int:user_id>/reset-password",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def reset_password(user_id):
    user = User.query.get_or_404(user_id)

    if user.role == "admin":
        flash(
            "Admin passwords cannot be reset from this page.",
            "warning"
        )

        return redirect(
            url_for("admin_users.index")
        )

    form = AdminResetPasswordForm()

    if form.validate_on_submit():
        user.set_password(
            form.new_password.data
        )

        db.session.commit()

        flash(
            f"Password for {user.username} was reset successfully.",
            "success"
        )

        return redirect(
            url_for("admin_users.index")
        )

    return render_template(
        "admin/reset_user_password.html",
        user=user,
        form=form
    )


@admin_users_bp.route(
    "/members/<int:member_id>/create-account",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def create_member_account(member_id):
    member = FamilyMember.query.get_or_404(
        member_id
    )

    if member.user_id is not None:
        flash(
            "This family member already has a linked login account.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.member_detail",
                member_id=member.id
            )
        )

    form = CreateMemberAccountForm()

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
                "admin/create_member_account.html",
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
                "admin/create_member_account.html",
                member=member,
                form=form
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

        db.session.commit()

        flash(
            f"Login account created successfully for {member.full_name}.",
            "success"
        )

        return redirect(
            url_for(
                "admin.member_detail",
                member_id=member.id
            )
        )

    if member.email and not form.email.data:
        form.email.data = member.email

    return render_template(
        "admin/create_member_account.html",
        member=member,
        form=form
    )


@admin_users_bp.route(
    "/members/<int:member_id>/unlink-account",
    methods=["POST"]
)
@login_required
@admin_required
def unlink_member_account(member_id):
    member = FamilyMember.query.get_or_404(
        member_id
    )

    if member.user_id is None:
        flash(
            "This family member does not have a linked login account.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.member_detail",
                member_id=member.id
            )
        )

    username = member.user.username

    member.user_id = None

    db.session.commit()

    flash(
        f"{username} was unlinked from {member.full_name}.",
        "success"
    )

    return redirect(
        url_for(
            "admin.member_detail",
            member_id=member.id
        )
    )


@admin_users_bp.route(
    "/<int:user_id>/link-account",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def link_existing_account(user_id):
    user = User.query.get_or_404(
        user_id
    )

    if user.role == "admin":
        flash(
            "Admin accounts cannot be linked to family member profiles.",
            "warning"
        )

        return redirect(
            url_for("admin_users.index")
        )

    already_linked = FamilyMember.query.filter_by(
        user_id=user.id
    ).first()

    if already_linked:
        flash(
            "This user account is already linked to a family member.",
            "warning"
        )

        return redirect(
            url_for("admin_users.index")
        )

    available_members = FamilyMember.query.filter(
        FamilyMember.user_id.is_(None)
    ).order_by(
        FamilyMember.full_name.asc()
    ).all()

    if not available_members:
        flash(
            "There are no unlinked family members available.",
            "warning"
        )

        return redirect(
            url_for("admin_users.index")
        )

    form = LinkExistingAccountForm()

    form.member_id.choices = [
        (
            member.id,
            member.full_name
        )
        for member in available_members
    ]

    if form.validate_on_submit():
        member = FamilyMember.query.get_or_404(
            form.member_id.data
        )

        if member.user_id is not None:
            flash(
                "That family member already has a linked account.",
                "danger"
            )

            return redirect(
                url_for(
                    "admin_users.link_existing_account",
                    user_id=user.id
                )
            )

        member.user_id = user.id

        db.session.commit()

        flash(
            f"{user.username} was linked to {member.full_name} successfully.",
            "success"
        )

        return redirect(
            url_for("admin_users.index")
        )

    return render_template(
        "admin/link_existing_account.html",
        user=user,
        form=form
    )


@admin_users_bp.route(
    "/<int:user_id>/delete",
    methods=["POST"]
)
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(
        user_id
    )

    if user.role == "admin":
        flash(
            "Admin accounts cannot be deleted from this page.",
            "warning"
        )

        return redirect(
            url_for("admin_users.index")
        )

    linked_member = FamilyMember.query.filter_by(
        user_id=user.id
    ).first()

    if linked_member:
        flash(
            "This account is linked to a family member. "
            "Unlink it before deleting the account.",
            "danger"
        )

        return redirect(
            url_for("admin_users.index")
        )

    has_activity_records = Activity.query.filter_by(
        created_by=user.id
    ).first() is not None

    has_event_records = Event.query.filter_by(
        created_by=user.id
    ).first() is not None

    has_announcement_records = Announcement.query.filter_by(
        created_by=user.id
    ).first() is not None

    has_gallery_records = GalleryPhoto.query.filter_by(
        uploaded_by=user.id
    ).first() is not None

    has_document_records = Document.query.filter_by(
        uploaded_by=user.id
    ).first() is not None

    has_history_records = FamilyHistory.query.filter_by(
        created_by=user.id
    ).first() is not None

    has_owned_records = any(
        [
            has_activity_records,
            has_event_records,
            has_announcement_records,
            has_gallery_records,
            has_document_records,
            has_history_records
        ]
    )

    if has_owned_records:
        flash(
            "This account owns family records and cannot be deleted yet.",
            "danger"
        )

        return redirect(
            url_for("admin_users.index")
        )

    username = user.username

    db.session.delete(user)
    db.session.commit()

    flash(
        f"{username} was deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin_users.index")
    )