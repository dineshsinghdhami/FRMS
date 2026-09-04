from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.extensions import db
from app.forms.timeline import TimelineEventForm
from app.models.family_member import FamilyMember
from app.models.timeline_event import TimelineEvent
from app.utilities.decorators import admin_required


timeline_bp = Blueprint(
    "timeline",
    __name__,
    url_prefix="/admin"
)


@timeline_bp.route(
    "/members/<int:member_id>/timeline",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def member_timeline(member_id):
    member = FamilyMember.query.get_or_404(member_id)

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
            url_for(
                "timeline.member_timeline",
                member_id=member.id
            )
        )

    timeline_events = TimelineEvent.query.filter_by(
        member_id=member.id
    ).order_by(
        TimelineEvent.event_date.asc().nullslast(),
        TimelineEvent.year.asc().nullslast(),
        TimelineEvent.created_at.asc()
    ).all()

    return render_template(
        "admin/member_timeline.html",
        member=member,
        form=form,
        timeline_events=timeline_events
    )


@timeline_bp.route(
    "/timeline/<int:event_id>/edit",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def edit_timeline_event(event_id):
    event = TimelineEvent.query.get_or_404(event_id)

    member = event.member

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
            url_for(
                "timeline.member_timeline",
                member_id=member.id
            )
        )

    return render_template(
        "admin/edit_timeline_event.html",
        form=form,
        event=event,
        member=member
    )


@timeline_bp.route(
    "/timeline/<int:event_id>/delete",
    methods=["POST"]
)
@login_required
@admin_required
def delete_timeline_event(event_id):
    event = TimelineEvent.query.get_or_404(event_id)

    member_id = event.member_id
    event_title = event.title

    db.session.delete(event)
    db.session.commit()

    flash(
        f"{event_title} was deleted successfully.",
        "success"
    )

    return redirect(
        url_for(
            "timeline.member_timeline",
            member_id=member_id
        )
    )