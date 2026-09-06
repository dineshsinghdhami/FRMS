import os

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import login_required

from app.extensions import db
from app.forms.member import FamilyMemberForm
from app.forms.relationship import RelationshipForm
from app.models.activity import Activity
from app.models.announcement import Announcement
from app.models.document import Document
from app.models.event import Event
from app.models.family_history import FamilyHistory
from app.models.family_member import FamilyMember
from app.models.gallery_photo import GalleryPhoto
from app.models.relationship import Relationship
from app.models.user import User
from app.utilities.decorators import admin_required


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


def get_reverse_relationship(
    relationship_type,
    member,
    related_member
):
    if relationship_type == "Father":
        if related_member.gender == "Female":
            return "Daughter"
        return "Son"

    if relationship_type == "Mother":
        if related_member.gender == "Female":
            return "Daughter"
        return "Son"

    if relationship_type == "Son":
        if member.gender == "Female":
            return "Mother"
        return "Father"

    if relationship_type == "Daughter":
        if member.gender == "Female":
            return "Mother"
        return "Father"

    if relationship_type == "Husband":
        return "Wife"

    if relationship_type == "Wife":
        return "Husband"

    if relationship_type == "Spouse":
        return "Spouse"

    if relationship_type == "Brother":
        if related_member.gender == "Female":
            return "Sister"
        return "Brother"

    if relationship_type == "Sister":
        if related_member.gender == "Male":
            return "Brother"
        return "Sister"

    if relationship_type == "Grandfather":
        return "Grandchild"

    if relationship_type == "Grandmother":
        return "Grandchild"

    if relationship_type == "Grandchild":
        if member.gender == "Female":
            return "Grandmother"
        return "Grandfather"

    if relationship_type == "Cousin":
        return "Cousin"

    return None


def assign_generation_from_relationship(
    member,
    related_member,
    relationship_type
):
    if member.generation is not None and related_member.generation is not None:
        return False

    if relationship_type in ["Father", "Mother"]:
        if member.generation is None and related_member.generation is not None:
            member.generation = related_member.generation - 1
            return True

        if member.generation is not None and related_member.generation is None:
            related_member.generation = member.generation + 1
            return True

    if relationship_type in ["Son", "Daughter"]:
        if member.generation is None and related_member.generation is not None:
            member.generation = related_member.generation + 1
            return True

        if member.generation is not None and related_member.generation is None:
            related_member.generation = member.generation - 1
            return True

    if relationship_type in ["Grandfather", "Grandmother"]:
        if member.generation is None and related_member.generation is not None:
            member.generation = related_member.generation - 2
            return True

        if member.generation is not None and related_member.generation is None:
            related_member.generation = member.generation + 2
            return True

    if relationship_type == "Grandchild":
        if member.generation is None and related_member.generation is not None:
            member.generation = related_member.generation + 2
            return True

        if member.generation is not None and related_member.generation is None:
            related_member.generation = member.generation - 2
            return True

    if relationship_type in [
        "Husband",
        "Wife",
        "Spouse",
        "Brother",
        "Sister",
        "Cousin"
    ]:
        if member.generation is None and related_member.generation is not None:
            member.generation = related_member.generation
            return True

        if member.generation is not None and related_member.generation is None:
            related_member.generation = member.generation
            return True

    return False


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    inactive_users = User.query.filter_by(is_active=False).count()
    admin_users = User.query.filter_by(role="admin").count()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        active_users=active_users,
        inactive_users=inactive_users,
        admin_users=admin_users
    )


@admin_bp.route("/members")
@login_required
@admin_required
def members():
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
        FamilyMember.created_at.desc()
    ).all()

    return render_template(
        "admin/members.html",
        family_members=family_members,
        search=search
    )


@admin_bp.route("/family-tree")
@login_required
@admin_required
def family_tree():
    generation_filter = request.args.get(
        "generation",
        type=int
    )

    query = FamilyMember.query

    if generation_filter:
        query = query.filter_by(
            generation=generation_filter
        )

    family_members = query.order_by(
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
        "admin/family_tree.html",
        family_members=family_members,
        generations=generations,
        generation_filter=generation_filter,
        tree_connections=tree_connections
    )


@admin_bp.route("/members/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_member():
    form = FamilyMemberForm()

    if form.validate_on_submit():
        member = FamilyMember(
            full_name=form.full_name.data.strip(),
            date_of_birth=form.date_of_birth.data,
            gender=form.gender.data or None,
            blood_group=form.blood_group.data or None,
            phone=form.phone.data.strip() if form.phone.data else None,
            email=form.email.data.strip() if form.email.data else None,
            permanent_address=(
                form.permanent_address.data.strip()
                if form.permanent_address.data
                else None
            ),
            current_address=(
                form.current_address.data.strip()
                if form.current_address.data
                else None
            ),
            occupation=(
                form.occupation.data.strip()
                if form.occupation.data
                else None
            ),
            marital_status=form.marital_status.data or None,
            emergency_contact=(
                form.emergency_contact.data.strip()
                if form.emergency_contact.data
                else None
            ),
            generation=form.generation.data,
            bio=form.bio.data.strip() if form.bio.data else None
        )

        db.session.add(member)
        db.session.commit()

        flash(
            "Family member added successfully.",
            "success"
        )

        return redirect(
            url_for(
                "admin.member_detail",
                member_id=member.id
            )
        )

    return render_template(
        "admin/add_member.html",
        form=form
    )


@admin_bp.route(
    "/members/<int:member_id>",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def member_detail(member_id):
    member = FamilyMember.query.get_or_404(member_id)

    relationship_form = RelationshipForm()

    available_members = FamilyMember.query.filter(
        FamilyMember.id != member.id
    ).order_by(
        FamilyMember.full_name.asc()
    ).all()

    relationship_form.related_member_id.choices = [
        (
            family_member.id,
            family_member.full_name
        )
        for family_member in available_members
    ]

    if relationship_form.validate_on_submit():
        related_member = FamilyMember.query.get_or_404(
            relationship_form.related_member_id.data
        )

        relationship_type = relationship_form.relationship_type.data

        existing_relationship = Relationship.query.filter_by(
            member_id=member.id,
            related_member_id=related_member.id,
            relationship_type=relationship_type
        ).first()

        if existing_relationship:
            flash(
                "This relationship already exists.",
                "warning"
            )

            return redirect(
                url_for(
                    "admin.member_detail",
                    member_id=member.id
                )
            )

        relationship = Relationship(
            member_id=member.id,
            related_member_id=related_member.id,
            relationship_type=relationship_type
        )

        db.session.add(relationship)

        reverse_type = get_reverse_relationship(
            relationship_type,
            member,
            related_member
        )

        if reverse_type:
            reverse_exists = Relationship.query.filter_by(
                member_id=related_member.id,
                related_member_id=member.id,
                relationship_type=reverse_type
            ).first()

            if not reverse_exists:
                reverse_relationship = Relationship(
                    member_id=related_member.id,
                    related_member_id=member.id,
                    relationship_type=reverse_type
                )

                db.session.add(reverse_relationship)

        generation_updated = assign_generation_from_relationship(
            member,
            related_member,
            relationship_type
        )

        db.session.commit()

        if generation_updated:
            flash(
                "Relationship added and generation assigned automatically.",
                "success"
            )
        else:
            flash(
                "Relationship added successfully.",
                "success"
            )

        return redirect(
            url_for(
                "admin.member_detail",
                member_id=member.id
            )
        )

    relationships = Relationship.query.filter_by(
        member_id=member.id
    ).order_by(
        Relationship.created_at.desc()
    ).all()

    return render_template(
        "admin/member_detail.html",
        member=member,
        relationship_form=relationship_form,
        relationships=relationships
    )


@admin_bp.route(
    "/members/<int:member_id>/edit",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def edit_member(member_id):
    member = FamilyMember.query.get_or_404(member_id)

    form = FamilyMemberForm(obj=member)

    if form.validate_on_submit():
        member.full_name = form.full_name.data.strip()
        member.date_of_birth = form.date_of_birth.data
        member.gender = form.gender.data or None
        member.blood_group = form.blood_group.data or None

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

        member.marital_status = (
            form.marital_status.data or None
        )

        member.emergency_contact = (
            form.emergency_contact.data.strip()
            if form.emergency_contact.data
            else None
        )

        member.generation = form.generation.data

        member.bio = (
            form.bio.data.strip()
            if form.bio.data
            else None
        )

        db.session.commit()

        flash(
            "Family member updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "admin.member_detail",
                member_id=member.id
            )
        )

    return render_template(
        "admin/edit_member.html",
        form=form,
        member=member
    )


@admin_bp.route(
    "/members/<int:member_id>/delete",
    methods=["POST"]
)
@login_required
@admin_required
def delete_member(member_id):
    member = FamilyMember.query.get_or_404(member_id)

    if member.user:
        flash(
            "This family member has a linked login account. "
            "Unlink or manage the account before deleting the profile.",
            "danger"
        )

        return redirect(
            url_for(
                "admin.member_detail",
                member_id=member.id
            )
        )

    Relationship.query.filter(
        db.or_(
            Relationship.member_id == member.id,
            Relationship.related_member_id == member.id
        )
    ).delete(
        synchronize_session=False
    )

    member_name = member.full_name

    db.session.delete(member)
    db.session.commit()

    flash(
        f"{member_name} was deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin.members")
    )


@admin_bp.route(
    "/members/<int:member_id>/delete-with-account",
    methods=["POST"]
)
@login_required
@admin_required
def delete_member_with_account(member_id):
    member = FamilyMember.query.get_or_404(member_id)

    if not member.user:
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

    user = member.user

    if user.role == "admin":
        flash(
            "Admin accounts cannot be deleted through member management.",
            "danger"
        )

        return redirect(
            url_for(
                "admin.member_detail",
                member_id=member.id
            )
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
            "This member account owns family records. "
            "Delete or reassign those records before deleting the account.",
            "danger"
        )

        return redirect(
            url_for(
                "admin.member_detail",
                member_id=member.id
            )
        )

    Relationship.query.filter(
        db.or_(
            Relationship.member_id == member.id,
            Relationship.related_member_id == member.id
        )
    ).delete(
        synchronize_session=False
    )

    member_name = member.full_name
    username = user.username

    member.user_id = None
    db.session.flush()

    db.session.delete(member)
    db.session.delete(user)
    db.session.commit()

    flash(
        f"{member_name} and the linked account {username} were deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin.members")
    )


@admin_bp.route("/activities")
@login_required
@admin_required
def activities():
    activities = Activity.query.order_by(
        Activity.activity_date.desc().nullslast(),
        Activity.created_at.desc()
    ).all()

    return render_template(
        "admin/activities.html",
        activities=activities
    )


@admin_bp.route(
    "/activities/<int:activity_id>/delete",
    methods=["POST"]
)
@login_required
@admin_required
def delete_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)

    activity_title = activity.title

    db.session.delete(activity)
    db.session.commit()

    flash(
        f"{activity_title} was deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin.activities")
    )


@admin_bp.route("/events")
@login_required
@admin_required
def events():
    events = Event.query.order_by(
        Event.event_date.asc(),
        Event.event_time.asc().nullslast()
    ).all()

    return render_template(
        "admin/events.html",
        events=events
    )


@admin_bp.route(
    "/events/<int:event_id>/delete",
    methods=["POST"]
)
@login_required
@admin_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)

    event_title = event.title

    db.session.delete(event)
    db.session.commit()

    flash(
        f"{event_title} was deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin.events")
    )


@admin_bp.route("/announcements")
@login_required
@admin_required
def announcements():
    announcements = Announcement.query.order_by(
        Announcement.created_at.desc()
    ).all()

    return render_template(
        "admin/announcements.html",
        announcements=announcements
    )


@admin_bp.route(
    "/announcements/<int:announcement_id>/delete",
    methods=["POST"]
)
@login_required
@admin_required
def delete_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(
        announcement_id
    )

    announcement_title = announcement.title

    db.session.delete(announcement)
    db.session.commit()

    flash(
        f"{announcement_title} was deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin.announcements")
    )


@admin_bp.route("/gallery")
@login_required
@admin_required
def gallery():
    photos = GalleryPhoto.query.order_by(
        GalleryPhoto.uploaded_at.desc()
    ).all()

    return render_template(
        "admin/gallery.html",
        photos=photos
    )


@admin_bp.route("/gallery/<int:photo_id>/image")
@login_required
@admin_required
def gallery_photo_image(photo_id):
    photo = GalleryPhoto.query.get_or_404(
        photo_id
    )

    upload_folder = os.path.join(
        current_app.root_path,
        "uploads",
        "gallery"
    )

    return send_from_directory(
        upload_folder,
        photo.filename
    )


@admin_bp.route(
    "/gallery/<int:photo_id>/delete",
    methods=["POST"]
)
@login_required
@admin_required
def delete_gallery_photo(photo_id):
    photo = GalleryPhoto.query.get_or_404(photo_id)

    photo_title = photo.title

    photo_path = os.path.join(
        current_app.root_path,
        "uploads",
        "gallery",
        photo.filename
    )

    if os.path.exists(photo_path):
        os.remove(photo_path)

    db.session.delete(photo)
    db.session.commit()

    flash(
        f"{photo_title} was deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin.gallery")
    )