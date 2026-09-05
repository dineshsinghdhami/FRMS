from datetime import datetime, timezone

from app.extensions import db


class Announcement(db.Model):
    __tablename__ = "announcements"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(150),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    category = db.Column(
        db.String(80),
        nullable=False,
        default="General"
    )

    priority = db.Column(
        db.String(30),
        nullable=False,
        default="Normal"
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
            "announcements",
            lazy=True
        )
    )

    def __repr__(self):
        return f"<Announcement {self.title}>"