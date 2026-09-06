from datetime import datetime, timezone

from app.extensions import db


class FamilyHistory(db.Model):
    __tablename__ = "family_history"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    year = db.Column(
        db.Integer,
        nullable=True
    )

    location = db.Column(
        db.String(200),
        nullable=True
    )

    category = db.Column(
        db.String(80),
        nullable=False,
        default="General"
    )

    privacy_level = db.Column(
        db.String(30),
        nullable=False,
        default="Family"
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
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

    creator = db.relationship(
        "User",
        backref=db.backref(
            "family_history_records",
            lazy=True
        )
    )

    def __repr__(self):
        return f"<FamilyHistory {self.title}>"