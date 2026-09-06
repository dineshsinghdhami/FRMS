from flask import Blueprint, render_template
from flask_login import login_required

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