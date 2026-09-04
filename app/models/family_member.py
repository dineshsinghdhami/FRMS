from datetime import datetime, timezone

from app.extensions import db


class FamilyMember(db.Model):
    __tablename__ = "family_members"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=True
    )

    full_name = db.Column(
        db.String(150),
        nullable=False
    )

    date_of_birth = db.Column(
        db.Date,
        nullable=True
    )

    gender = db.Column(
        db.String(20),
        nullable=True
    )

    blood_group = db.Column(
        db.String(10),
        nullable=True
    )

    phone = db.Column(
        db.String(30),
        nullable=True
    )

    email = db.Column(
        db.String(120),
        nullable=True
    )

    permanent_address = db.Column(
        db.String(255),
        nullable=True
    )

    current_address = db.Column(
        db.String(255),
        nullable=True
    )

    occupation = db.Column(
        db.String(120),
        nullable=True
    )

    marital_status = db.Column(
        db.String(30),
        nullable=True
    )

    emergency_contact = db.Column(
        db.String(120),
        nullable=True
    )

    bio = db.Column(
        db.Text,
        nullable=True
    )

    profile_photo = db.Column(
        db.String(255),
        nullable=True
    )

    generation = db.Column(
        db.Integer,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "family_member",
            uselist=False
        )
    )

    def __repr__(self):
        return f"<FamilyMember {self.full_name}>"