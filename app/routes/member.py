import os
import uuid

from flask import Blueprint, current_app, flash, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app.extensions import db
from app.forms.account import ChangePasswordForm
from app.forms.activity import ActivityForm
from app.forms.announcement import AnnouncementForm
from app.forms.document import DocumentForm
from app.forms.event import EventForm
from app.forms.gallery import GalleryPhotoForm
from app.forms.member import FamilyMemberForm
from app.forms.timeline import TimelineEventForm
from app.models.activity import Activity
from app.models.announcement import Announcement
from app.models.document import Document
from app.models.event import Event
from app.models.family_member import FamilyMember
from app.models.gallery_photo import GalleryPhoto
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


def save_gallery_photo(photo_file):
    upload_folder = os.path.join(
        current_app.root_path,
        "static",
        "uploads",
        "gallery"
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    original_filename = secure_filename(
        photo_file.filename
    )

    extension = os.path.splitext(
        original_filename
    )[1].lower()

    unique_filename = f"{uuid.uuid4().hex}{extension}"

    file_path = os.path.join(
        upload_folder,
        unique_filename
    )

    photo_file.save(
        file_path
    )

    return unique_filename, original_filename


def save_document_file(document_file):
    upload_folder = os.path.join(
        current_app.root_path,
        "uploads",
        "documents"
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    original_filename = secure_filename(
        document_file.filename
    )

    extension = os.path.splitext(
        original_filename
    )[1].lower()

    unique_filename = f"{uuid.uuid4().hex}{extension}"

    file_path = os.path.join(
        upload_folder,
        unique_filename
    )

    document_file.save(
        file_path
    )

    return unique_filename, original_filename


@member_bp.route("/dashboard")
@login_required
def dashboard():
    if not member_only():
        return render_template("errors/403.html"), 403

    member = get_current_family_member()

    return render_template(
        "member/dashboard.html",
        member=member
    )


@member_bp.route("/profile")
@login_required
def profile():
    if not member_only():
        return render_template("errors/403.html"), 403

    member = get_current_family_member()

    return render_template(
        "member/profile.html",
        member=member
    )


@member_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if not member_only():
        return render_template("errors/403.html"), 403

    member = get_current_family_member()
    form = FamilyMemberForm(obj=member)

    if form.validate_on_submit():
        member.full_name = form.full_name.data.strip()
        member.date_of_birth = form.date_of_birth.data
        member.gender = form.gender.data
        member.blood_group = form.blood_group.data
        member.phone = form.phone.data.strip() if form.phone.data else None
        member.email = form.email.data.strip() if form.email.data else None
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
        member.bio = form.bio.data.strip() if form.bio.data else None

        db.session.commit()

        flash("Profile updated successfully.", "success")

        return redirect(
            url_for("member.profile")
        )

    return render_template(
        "member/edit_profile.html",
        member=member,
        form=form
    )


@member_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if not member_only():
        return render_template("errors/403.html"), 403

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
        return render_template("errors/403.html"), 403

    member = get_current_family_member()
    form = TimelineEventForm()

    if form.validate_on_submit():
        event = TimelineEvent(
            member_id=member.id,
            title=form.title.data.strip(),
            description=form.description.data.strip() if form.description.data else None,
            event_date=form.event_date.data,
            year=form.year.data,
            category=form.category.data,
            location=form.location.data.strip() if form.location.data else None,
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


@member_bp.route("/timeline/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
def edit_timeline_event(event_id):
    if not member_only():
        return render_template("errors/403.html"), 403

    member = get_current_family_member()
    event = TimelineEvent.query.get_or_404(event_id)

    if event.member_id != member.id:
        return render_template("errors/403.html"), 403

    form = TimelineEventForm(obj=event)

    if form.validate_on_submit():
        event.title = form.title.data.strip()
        event.description = form.description.data.strip() if form.description.data else None
        event.event_date = form.event_date.data
        event.year = form.year.data
        event.category = form.category.data
        event.location = form.location.data.strip() if form.location.data else None
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


@member_bp.route("/timeline/<int:event_id>/delete", methods=["POST"])
@login_required
def delete_timeline_event(event_id):
    if not member_only():
        return render_template("errors/403.html"), 403

    member = get_current_family_member()
    event = TimelineEvent.query.get_or_404(event_id)

    if event.member_id != member.id:
        return render_template("errors/403.html"), 403

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
        return render_template("errors/403.html"), 403

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
        return render_template("errors/403.html"), 403

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
        return render_template("errors/403.html"), 403

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


@member_bp.route("/activities", methods=["GET", "POST"])
@login_required
def activities():
    if not member_only():
        return render_template("errors/403.html"), 403

    form = ActivityForm()

    if form.validate_on_submit():
        activity = Activity(
            title=form.title.data.strip(),
            description=form.description.data.strip() if form.description.data else None,
            activity_date=form.activity_date.data,
            location=form.location.data.strip() if form.location.data else None,
            category=form.category.data,
            privacy_level=form.privacy_level.data,
            created_by=current_user.id
        )

        db.session.add(activity)
        db.session.commit()

        flash("Activity added successfully.", "success")

        return redirect(
            url_for("member.activities")
        )

    activities = Activity.query.filter(
        db.or_(
            Activity.privacy_level == "Family",
            Activity.created_by == current_user.id
        )
    ).order_by(
        Activity.activity_date.desc().nullslast(),
        Activity.created_at.desc()
    ).all()

    return render_template(
        "member/activities.html",
        form=form,
        activities=activities
    )


@member_bp.route("/activities/<int:activity_id>/edit", methods=["GET", "POST"])
@login_required
def edit_activity(activity_id):
    if not member_only():
        return render_template("errors/403.html"), 403

    activity = Activity.query.get_or_404(activity_id)

    if activity.created_by != current_user.id:
        return render_template("errors/403.html"), 403

    form = ActivityForm(obj=activity)

    if form.validate_on_submit():
        activity.title = form.title.data.strip()
        activity.description = form.description.data.strip() if form.description.data else None
        activity.activity_date = form.activity_date.data
        activity.location = form.location.data.strip() if form.location.data else None
        activity.category = form.category.data
        activity.privacy_level = form.privacy_level.data

        db.session.commit()

        flash("Activity updated successfully.", "success")

        return redirect(
            url_for("member.activities")
        )

    return render_template(
        "member/edit_activity.html",
        activity=activity,
        form=form
    )


@member_bp.route("/activities/<int:activity_id>/delete", methods=["POST"])
@login_required
def delete_activity(activity_id):
    if not member_only():
        return render_template("errors/403.html"), 403

    activity = Activity.query.get_or_404(activity_id)

    if activity.created_by != current_user.id:
        return render_template("errors/403.html"), 403

    activity_title = activity.title

    db.session.delete(activity)
    db.session.commit()

    flash(
        f"{activity_title} was deleted successfully.",
        "success"
    )

    return redirect(
        url_for("member.activities")
    )


@member_bp.route("/events", methods=["GET", "POST"])
@login_required
def events():
    if not member_only():
        return render_template("errors/403.html"), 403

    form = EventForm()

    if form.validate_on_submit():
        event = Event(
            title=form.title.data.strip(),
            description=form.description.data.strip() if form.description.data else None,
            event_date=form.event_date.data,
            event_time=form.event_time.data,
            location=form.location.data.strip() if form.location.data else None,
            category=form.category.data,
            privacy_level=form.privacy_level.data,
            created_by=current_user.id
        )

        db.session.add(event)
        db.session.commit()

        flash("Event added successfully.", "success")

        return redirect(
            url_for("member.events")
        )

    events = Event.query.filter(
        db.or_(
            Event.privacy_level == "Family",
            Event.created_by == current_user.id
        )
    ).order_by(
        Event.event_date.asc(),
        Event.event_time.asc().nullslast()
    ).all()

    return render_template(
        "member/events.html",
        form=form,
        events=events
    )


@member_bp.route("/events/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
def edit_event(event_id):
    if not member_only():
        return render_template("errors/403.html"), 403

    event = Event.query.get_or_404(event_id)

    if event.created_by != current_user.id:
        return render_template("errors/403.html"), 403

    form = EventForm(obj=event)

    if form.validate_on_submit():
        event.title = form.title.data.strip()
        event.description = form.description.data.strip() if form.description.data else None
        event.event_date = form.event_date.data
        event.event_time = form.event_time.data
        event.location = form.location.data.strip() if form.location.data else None
        event.category = form.category.data
        event.privacy_level = form.privacy_level.data

        db.session.commit()

        flash("Event updated successfully.", "success")

        return redirect(
            url_for("member.events")
        )

    return render_template(
        "member/edit_event.html",
        event=event,
        form=form
    )


@member_bp.route("/events/<int:event_id>/delete", methods=["POST"])
@login_required
def delete_event(event_id):
    if not member_only():
        return render_template("errors/403.html"), 403

    event = Event.query.get_or_404(event_id)

    if event.created_by != current_user.id:
        return render_template("errors/403.html"), 403

    event_title = event.title

    db.session.delete(event)
    db.session.commit()

    flash(
        f"{event_title} was deleted successfully.",
        "success"
    )

    return redirect(
        url_for("member.events")
    )


@member_bp.route("/announcements", methods=["GET", "POST"])
@login_required
def announcements():
    if not member_only():
        return render_template("errors/403.html"), 403

    form = AnnouncementForm()

    if form.validate_on_submit():
        announcement = Announcement(
            title=form.title.data.strip(),
            message=form.message.data.strip(),
            category=form.category.data,
            priority=form.priority.data,
            privacy_level=form.privacy_level.data,
            created_by=current_user.id
        )

        db.session.add(announcement)
        db.session.commit()

        flash("Announcement added successfully.", "success")

        return redirect(
            url_for("member.announcements")
        )

    announcements = Announcement.query.filter(
        db.or_(
            Announcement.privacy_level == "Family",
            Announcement.created_by == current_user.id
        )
    ).order_by(
        Announcement.created_at.desc()
    ).all()

    return render_template(
        "member/announcements.html",
        form=form,
        announcements=announcements
    )


@member_bp.route("/announcements/<int:announcement_id>/edit", methods=["GET", "POST"])
@login_required
def edit_announcement(announcement_id):
    if not member_only():
        return render_template("errors/403.html"), 403

    announcement = Announcement.query.get_or_404(
        announcement_id
    )

    if announcement.created_by != current_user.id:
        return render_template("errors/403.html"), 403

    form = AnnouncementForm(obj=announcement)

    if form.validate_on_submit():
        announcement.title = form.title.data.strip()
        announcement.message = form.message.data.strip()
        announcement.category = form.category.data
        announcement.priority = form.priority.data
        announcement.privacy_level = form.privacy_level.data

        db.session.commit()

        flash(
            "Announcement updated successfully.",
            "success"
        )

        return redirect(
            url_for("member.announcements")
        )

    return render_template(
        "member/edit_announcement.html",
        announcement=announcement,
        form=form
    )


@member_bp.route("/announcements/<int:announcement_id>/delete", methods=["POST"])
@login_required
def delete_announcement(announcement_id):
    if not member_only():
        return render_template("errors/403.html"), 403

    announcement = Announcement.query.get_or_404(
        announcement_id
    )

    if announcement.created_by != current_user.id:
        return render_template("errors/403.html"), 403

    announcement_title = announcement.title

    db.session.delete(announcement)
    db.session.commit()

    flash(
        f"{announcement_title} was deleted successfully.",
        "success"
    )

    return redirect(
        url_for("member.announcements")
    )


@member_bp.route("/gallery", methods=["GET", "POST"])
@login_required
def gallery():
    if not member_only():
        return render_template("errors/403.html"), 403

    form = GalleryPhotoForm()

    if form.validate_on_submit():
        unique_filename, original_filename = save_gallery_photo(
            form.photo.data
        )

        photo = GalleryPhoto(
            title=form.title.data.strip(),
            description=form.description.data.strip() if form.description.data else None,
            filename=unique_filename,
            original_filename=original_filename,
            category=form.category.data,
            privacy_level=form.privacy_level.data,
            uploaded_by=current_user.id
        )

        db.session.add(photo)
        db.session.commit()

        flash("Photo uploaded successfully.", "success")

        return redirect(
            url_for("member.gallery")
        )

    photos = GalleryPhoto.query.filter(
        db.or_(
            GalleryPhoto.privacy_level == "Family",
            GalleryPhoto.uploaded_by == current_user.id
        )
    ).order_by(
        GalleryPhoto.uploaded_at.desc()
    ).all()

    return render_template(
        "member/gallery.html",
        form=form,
        photos=photos
    )


@member_bp.route("/gallery/<int:photo_id>/delete", methods=["POST"])
@login_required
def delete_gallery_photo(photo_id):
    if not member_only():
        return render_template("errors/403.html"), 403

    photo = GalleryPhoto.query.get_or_404(photo_id)

    if photo.uploaded_by != current_user.id:
        return render_template("errors/403.html"), 403

    file_path = os.path.join(
        current_app.root_path,
        "static",
        "uploads",
        "gallery",
        photo.filename
    )

    if os.path.exists(file_path):
        os.remove(file_path)

    photo_title = photo.title

    db.session.delete(photo)
    db.session.commit()

    flash(
        f"{photo_title} was deleted successfully.",
        "success"
    )

    return redirect(
        url_for("member.gallery")
    )


@member_bp.route("/documents", methods=["GET", "POST"])
@login_required
def documents():
    if not member_only():
        return render_template("errors/403.html"), 403

    form = DocumentForm()

    if form.validate_on_submit():
        unique_filename, original_filename = save_document_file(
            form.document.data
        )

        document = Document(
            title=form.title.data.strip(),
            description=form.description.data.strip() if form.description.data else None,
            filename=unique_filename,
            original_filename=original_filename,
            document_type=form.document_type.data,
            privacy_level=form.privacy_level.data,
            uploaded_by=current_user.id
        )

        db.session.add(document)
        db.session.commit()

        flash(
            "Document uploaded successfully.",
            "success"
        )

        return redirect(
            url_for("member.documents")
        )

    documents = Document.query.filter(
        db.or_(
            Document.privacy_level == "Family",
            Document.uploaded_by == current_user.id
        )
    ).order_by(
        Document.uploaded_at.desc()
    ).all()

    return render_template(
        "member/documents.html",
        form=form,
        documents=documents
    )


@member_bp.route("/documents/<int:document_id>/download")
@login_required
def download_document(document_id):
    if not member_only():
        return render_template("errors/403.html"), 403

    document = Document.query.get_or_404(document_id)

    can_access = (
        document.privacy_level == "Family"
        or document.uploaded_by == current_user.id
    )

    if not can_access:
        return render_template("errors/403.html"), 403

    upload_folder = os.path.join(
        current_app.root_path,
        "uploads",
        "documents"
    )

    return send_from_directory(
        upload_folder,
        document.filename,
        as_attachment=True,
        download_name=document.original_filename
    )

@member_bp.route(
    "/documents/<int:document_id>/delete",
    methods=["POST"]
)
@login_required
def delete_document(document_id):
    if not member_only():
        return render_template("errors/403.html"), 403

    document = Document.query.get_or_404(document_id)

    if document.uploaded_by != current_user.id:
        return render_template("errors/403.html"), 403

    file_path = os.path.join(
        current_app.root_path,
        "uploads",
        "documents",
        document.filename
    )

    if os.path.exists(file_path):
        os.remove(file_path)

    document_title = document.title

    db.session.delete(document)
    db.session.commit()

    flash(
        f"{document_title} was deleted successfully.",
        "success"
    )

    return redirect(
        url_for("member.documents")
    )