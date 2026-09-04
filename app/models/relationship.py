from datetime import datetime, timezone

from app.extensions import db


class Relationship(db.Model):
    __tablename__ = "relationships"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    member_id = db.Column(
        db.Integer,
        db.ForeignKey("family_members.id"),
        nullable=False
    )

    related_member_id = db.Column(
        db.Integer,
        db.ForeignKey("family_members.id"),
        nullable=False
    )

    relationship_type = db.Column(
        db.String(50),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    member = db.relationship(
        "FamilyMember",
        foreign_keys=[member_id],
        backref="relationships_from"
    )

    related_member = db.relationship(
        "FamilyMember",
        foreign_keys=[related_member_id],
        backref="relationships_to"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "member_id",
            "related_member_id",
            "relationship_type",
            name="uq_member_relationship"
        ),
    )

    def __repr__(self):
        return (
            f"<Relationship "
            f"{self.member_id} "
            f"{self.relationship_type} "
            f"{self.related_member_id}>"
        )