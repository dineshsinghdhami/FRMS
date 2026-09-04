from datetime import datetime, timezone

from app.extensions import db


class TimelineEvent(db.Model):
    __tablename__ = "timeline_events"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    member_id = db.Column(
        db.Integer,
        db.ForeignKey("family_members.id"),
        nullable=False,
        index=True
    )

    title = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    event_date = db.Column(
        db.Date,
        nullable=True
    )

    year = db.Column(
        db.Integer,
        nullable=True
    )

    category = db.Column(
        db.String(50),
        nullable=False,
        default="Other"
    )

    location = db.Column(
        db.String(150),
        nullable=True
    )

    privacy_level = db.Column(
        db.String(30),
        nullable=False,
        default="Family"
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

    member = db.relationship(
        "FamilyMember",
        backref=db.backref(
            "timeline_events",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )

    def __repr__(self):
        return f"<TimelineEvent {self.title}>"