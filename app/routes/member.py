from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms.account import ChangePasswordForm
from app.forms.member import FamilyMemberForm
from app.forms.timeline import TimelineEventForm
from app.models.family_member import FamilyMember
from app.models.relationship import Relationship
from app.models.timeline_event import TimelineEvent


member_bp = Blueprint(
    "member",
    __name__,
    url_prefix="/member"
)


def get_current_family_member():
    return FamilyMember.query.filter_by(
        user_id=current_user.id
    ).first_or_404()


def member_only():
    return current_user.role == "member"


@member_bp.route("/dashboard")
@login_required
def dashboard():
    if not member_only():
        return render_template(
            "errors/403.html"
        ), 403

    member = get_current_family_member()

    return render_template(
        "member/dashboard.html",
        member=member
    )


@member_bp.route("/profile")
@login_required
def profile():
    if not member_only():
        return render_template(
            "errors/403.html"
        ), 403

    member = get_current_family_member()

    return render_template(
        "member/profile.html",
        member=member
    )


@member_bp.route(
    "/profile/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_profile():
    if not member_only():
        return render_template(
            "errors/403.html"
        ), 403

    member = get_current_family_member()

    form = FamilyMemberForm(obj=member)

    if form.validate_on_submit():
        member.full_name = form.full_name.data.strip()
        member.date_of_birth = form.date_of_birth.data
        member.gender = form.gender.data
        member.blood_group = form.blood_group.data

        member.phone = (
            form.phone.data.strip()
            if form.phone.data
            else None
        )

        member.email = (
            form.email.data.strip()
            if form.email.data
            else None
        )

        member.permanent_address = (
            form.permanent_address.data.strip()
            if form.permanent_address.data
            else None
        )

        member.current_address = (
            form.current_address.data.strip()
            if form.current_address.data
            else None
        )

        member.occupation = (
            form.occupation.data.strip()
            if form.occupation.data
            else None
        )

        member.marital_status = form.marital_status.data

        member.emergency_contact = (
            form.emergency_contact.data.strip()
            if form.emergency_contact.data
            else None
        )

        member.bio = (
            form.bio.data.strip()
            if form.bio.data
            else None
        )

        db.session.commit()

        flash(
            "Profile updated successfully.",
            "success"
        )

        return redirect(
            url_for("member.profile")
        )

    return render_template(
        "member/edit_profile.html",
        member=member,
        form=form
    )


@member_bp.route(
    "/change-password",
    methods=["GET", "POST"]
)
@login_required
def change_password():
    if not member_only():
        return render_template(
            "errors/403.html"
        ), 403

    form = ChangePasswordForm()

    if form.validate_on_submit():

        if not current_user.check_password(
            form.current_password.data
        ):
            flash(
                "Current password is incorrect.",
                "danger"
            )

            return render_template(
                "member/change_password.html",
                form=form
            )

        if current_user.check_password(
            form.new_password.data
        ):
            flash(
                "New password must be different from your current password.",
                "warning"
            )

            return render_template(
                "member/change_password.html",
                form=form
            )

        current_user.set_password(
            form.new_password.data
        )

        db.session.commit()

        flash(
            "Password changed successfully.",
            "success"
        )

        return redirect(
            url_for("member.profile")
        )

    return render_template(
        "member/change_password.html",
        form=form
    )


@member_bp.route("/timeline", methods=["GET", "POST"])
@login_required
def timeline():
    if not member_only():
        return render_template(
            "errors/403.html"
        ), 403

    member = get_current_family_member()

    form = TimelineEventForm()

    if form.validate_on_submit():
        event = TimelineEvent(
            member_id=member.id,
            title=form.title.data.strip(),
            description=(
                form.description.data.strip()
                if form.description.data
                else None
            ),
            event_date=form.event_date.data,
            year=form.year.data,
            category=form.category.data,
            location=(
                form.location.data.strip()
                if form.location.data
                else None
            ),
            privacy_level=form.privacy_level.data
        )

        db.session.add(event)
        db.session.commit()

        flash(
            "Timeline event added successfully.",
            "success"
        )

        return redirect(
            url_for("member.timeline")
        )

    timeline_events = TimelineEvent.query.filter_by(
        member_id=member.id
    ).order_by(
        TimelineEvent.event_date.asc().nullslast(),
        TimelineEvent.year.asc().nullslast(),
        TimelineEvent.created_at.asc()
    ).all()

    return render_template(
        "member/timeline.html",
        member=member,
        form=form,
        timeline_events=timeline_events
    )


@member_bp.route(
    "/timeline/<int:event_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_timeline_event(event_id):
    if not member_only():
        return render_template(
            "errors/403.html"
        ), 403

    member = get_current_family_member()

    event = TimelineEvent.query.get_or_404(event_id)

    if event.member_id != member.id:
        return render_template(
            "errors/403.html"
        ), 403

    form = TimelineEventForm(obj=event)

    if form.validate_on_submit():
        event.title = form.title.data.strip()

        event.description = (
            form.description.data.strip()
            if form.description.data
            else None
        )

        event.event_date = form.event_date.data
        event.year = form.year.data
        event.category = form.category.data

        event.location = (
            form.location.data.strip()
            if form.location.data
            else None
        )

        event.privacy_level = form.privacy_level.data

        db.session.commit()

        flash(
            "Timeline event updated successfully.",
            "success"
        )

        return redirect(
            url_for("member.timeline")
        )

    return render_template(
        "member/edit_timeline_event.html",
        member=member,
        event=event,
        form=form
    )


@member_bp.route(
    "/timeline/<int:event_id>/delete",
    methods=["POST"]
)
@login_required
def delete_timeline_event(event_id):
    if not member_only():
        return render_template(
            "errors/403.html"
        ), 403

    member = get_current_family_member()

    event = TimelineEvent.query.get_or_404(event_id)

    if event.member_id != member.id:
        return render_template(
            "errors/403.html"
        ), 403

    event_title = event.title

    db.session.delete(event)
    db.session.commit()

    flash(
        f"{event_title} was deleted successfully.",
        "success"
    )

    return redirect(
        url_for("member.timeline")
    )


@member_bp.route("/family-tree")
@login_required
def family_tree():
    if not member_only():
        return render_template(
            "errors/403.html"
        ), 403

    family_members = FamilyMember.query.order_by(
        FamilyMember.generation.asc().nullslast(),
        FamilyMember.full_name.asc()
    ).all()

    generations = [
        generation[0]
        for generation in db.session.query(
            FamilyMember.generation
        )
        .filter(
            FamilyMember.generation.isnot(None)
        )
        .distinct()
        .order_by(
            FamilyMember.generation.asc()
        )
        .all()
    ]

    parent_child_relationships = Relationship.query.filter(
        Relationship.relationship_type.in_(
            ["Father", "Mother"]
        )
    ).all()

    tree_connections = []

    for relationship in parent_child_relationships:
        tree_connections.append(
            {
                "parent": relationship.member,
                "child": relationship.related_member,
                "relationship_type": relationship.relationship_type
            }
        )

    return render_template(
        "member/family_tree.html",
        family_members=family_members,
        generations=generations,
        tree_connections=tree_connections
    )


@member_bp.route("/family-members")
@login_required
def family_members():
    if not member_only():
        return render_template(
            "errors/403.html"
        ), 403

    search = request.args.get("search", "").strip()

    query = FamilyMember.query

    if search:
        search_term = f"%{search}%"

        query = query.filter(
            db.or_(
                FamilyMember.full_name.ilike(search_term),
                FamilyMember.occupation.ilike(search_term),
                FamilyMember.current_address.ilike(search_term),
                FamilyMember.permanent_address.ilike(search_term)
            )
        )

    family_members = query.order_by(
        FamilyMember.full_name.asc()
    ).all()

    return render_template(
        "member/family_members.html",
        family_members=family_members,
        search=search
    )


@member_bp.route("/family-members/<int:member_id>")
@login_required
def family_member_detail(member_id):
    if not member_only():
        return render_template(
            "errors/403.html"
        ), 403

    member = FamilyMember.query.get_or_404(member_id)

    relationships = Relationship.query.filter_by(
        member_id=member.id
    ).order_by(
        Relationship.relationship_type.asc()
    ).all()

    visible_timeline_events = TimelineEvent.query.filter(
        TimelineEvent.member_id == member.id,
        TimelineEvent.privacy_level == "Family"
    ).order_by(
        TimelineEvent.event_date.asc().nullslast(),
        TimelineEvent.year.asc().nullslast()
    ).all()

    return render_template(
        "member/family_member_detail.html",
        member=member,
        relationships=relationships,
        timeline_events=visible_timeline_events
    )