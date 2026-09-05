from datetime import datetime, timezone

from app.extensions import db


class GalleryPhoto(db.Model):
    __tablename__ = "gallery_photos"

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

    category = db.Column(
        db.String(80),
        nullable=False,
        default="Family"
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
            "gallery_photos",
            lazy=True
        )
    )

    def __repr__(self):
        return f"<GalleryPhoto {self.title}>"