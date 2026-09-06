import secrets
from datetime import datetime, timedelta, timezone

from app.extensions import db


class Invitation(db.Model):
    __tablename__ = "invitations"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    family_member_id = db.Column(
        db.Integer,
        db.ForeignKey("family_members.id"),
        nullable=False,
        index=True
    )

    token = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    expires_at = db.Column(
        db.DateTime,
        nullable=False
    )

    used_at = db.Column(
        db.DateTime,
        nullable=True
    )

    revoked_at = db.Column(
        db.DateTime,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    member = db.relationship(
        "FamilyMember",
        backref=db.backref(
            "invitations",
            lazy=True
        )
    )

    creator = db.relationship(
        "User",
        backref=db.backref(
            "created_invitations",
            lazy=True
        )
    )

    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(32)

    @staticmethod
    def default_expiry():
        return datetime.now(timezone.utc) + timedelta(days=7)

    def is_valid(self):
        now = datetime.now(timezone.utc)

        if self.used_at is not None:
            return False

        if self.revoked_at is not None:
            return False

        expires_at = self.expires_at

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(
                tzinfo=timezone.utc
            )

        return now < expires_at

    def __repr__(self):
        return f"<Invitation member={self.family_member_id}>"