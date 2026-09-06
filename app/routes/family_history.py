from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms.family_history import FamilyHistoryForm
from app.models.family_history import FamilyHistory


family_history_bp = Blueprint(
    "family_history",
    __name__,
    url_prefix="/member/family-history"
)


def member_only():
    return current_user.role == "member"


@family_history_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if not member_only():
        return render_template(
            "errors/403.html"
        ), 403

    form = FamilyHistoryForm()

    if form.validate_on_submit():
        history = FamilyHistory(
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            year=form.year.data,
            location=(
                form.location.data.strip()
                if form.location.data
                else None
            ),
            category=form.category.data,
            privacy_level=form.privacy_level.data,
            created_by=current_user.id
        )

        db.session.add(history)
        db.session.commit()

        flash(
            "Family history record added successfully.",
            "success"
        )

        return redirect(
            url_for("family_history.index")
        )

    history_records = FamilyHistory.query.filter(
        db.or_(
            FamilyHistory.privacy_level == "Family",
            FamilyHistory.created_by == current_user.id
        )
    ).order_by(
        FamilyHistory.year.asc().nullslast(),
        FamilyHistory.created_at.asc()
    ).all()

    return render_template(
        "member/family_history.html",
        form=form,
        history_records=history_records
    )


@family_history_bp.route(
    "/<int:history_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit(history_id):
    if not member_only():
        return render_template(
            "errors/403.html"
        ), 403

    history = FamilyHistory.query.get_or_404(
        history_id
    )

    if history.created_by != current_user.id:
        return render_template(
            "errors/403.html"
        ), 403

    form = FamilyHistoryForm(
        obj=history
    )

    if form.validate_on_submit():
        history.title = form.title.data.strip()
        history.description = form.description.data.strip()
        history.year = form.year.data

        history.location = (
            form.location.data.strip()
            if form.location.data
            else None
        )

        history.category = form.category.data
        history.privacy_level = form.privacy_level.data

        db.session.commit()

        flash(
            "Family history record updated successfully.",
            "success"
        )

        return redirect(
            url_for("family_history.index")
        )

    return render_template(
        "member/edit_family_history.html",
        history=history,
        form=form
    )


@family_history_bp.route(
    "/<int:history_id>/delete",
    methods=["POST"]
)
@login_required
def delete(history_id):
    if not member_only():
        return render_template(
            "errors/403.html"
        ), 403

    history = FamilyHistory.query.get_or_404(
        history_id
    )

    if history.created_by != current_user.id:
        return render_template(
            "errors/403.html"
        ), 403

    history_title = history.title

    db.session.delete(history)
    db.session.commit()

    flash(
        f"{history_title} was deleted successfully.",
        "success"
    )

    return redirect(
        url_for("family_history.index")
    )