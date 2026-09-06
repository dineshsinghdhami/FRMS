from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.extensions import db
from app.models.family_history import FamilyHistory
from app.utilities.decorators import admin_required


admin_family_history_bp = Blueprint(
    "admin_family_history",
    __name__,
    url_prefix="/admin/family-history"
)


@admin_family_history_bp.route("/")
@login_required
@admin_required
def index():
    history_records = FamilyHistory.query.order_by(
        FamilyHistory.year.asc().nullslast(),
        FamilyHistory.created_at.asc()
    ).all()

    return render_template(
        "admin/family_history.html",
        history_records=history_records
    )


@admin_family_history_bp.route(
    "/<int:history_id>/delete",
    methods=["POST"]
)
@login_required
@admin_required
def delete(history_id):
    history = FamilyHistory.query.get_or_404(
        history_id
    )

    history_title = history.title

    db.session.delete(history)
    db.session.commit()

    flash(
        f"{history_title} was deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin_family_history.index")
    )