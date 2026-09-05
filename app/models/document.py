from datetime import datetime, timezone

from app.extensions import db


class Document(db.Model):
    __tablename__ = "documents"

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

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    original_filename = db.Column(
        db.String(255),
        nullable=True
    )

    document_type = db.Column(
        db.String(80),
        nullable=False,
        default="Other"
    )

    privacy_level = db.Column(
        db.String(30),
        nullable=False,
        default="Family"
    )

    uploaded_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    uploaded_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    uploader = db.relationship(
        "User",
        backref=db.backref(
            "documents",
            lazy=True
        )
    )

    def __repr__(self):
        return f"<Document {self.title}>"