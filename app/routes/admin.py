from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.extensions import db
from app.forms.member import FamilyMemberForm
from app.models.family_member import FamilyMember
from app.models.user import User
from app.utilities.decorators import admin_required


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


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

        flash("Family member added successfully.", "success")

        return redirect(url_for("admin.add_member"))
    
    

    return render_template(
        "admin/add_member.html",
        form=form
    )
@admin_bp.route("/members")
@login_required
@admin_required
def members():
    from flask import request

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