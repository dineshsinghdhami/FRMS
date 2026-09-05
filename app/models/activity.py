from datetime import datetime, timezone

from app.extensions import db


class Activity(db.Model):
    __tablename__ = "activities"

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
        nullable=True
    )

    activity_date = db.Column(
        db.Date,
        nullable=True
    )

    location = db.Column(
        db.String(200),
        nullable=True
    )

    category = db.Column(
        db.String(80),
        nullable=False,
        default="Other"
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
            "activities",
            lazy=True
        )
    )

    def __repr__(self):
        return f"<Activity {self.title}>"