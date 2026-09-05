from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class GalleryPhotoForm(FlaskForm):
    title = StringField(
        "Photo Title",
        validators=[
            DataRequired(),
            Length(max=150)
        ]
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(max=2000)
        ]
    )

    photo = FileField(
        "Photo",
        validators=[
            FileRequired(),
            FileAllowed(
                ["jpg", "jpeg", "png", "webp"],
                "Only JPG, JPEG, PNG, and WEBP images are allowed."
            )
        ]
    )

    category = SelectField(
        "Category",
        choices=[
            ("Family", "Family"),
            ("Birthday", "Birthday"),
            ("Wedding", "Wedding"),
            ("Festival", "Festival"),
            ("Travel", "Travel"),
            ("Ceremony", "Ceremony"),
            ("Childhood", "Childhood"),
            ("Achievement", "Achievement"),
            ("Historical", "Historical"),
            ("Other", "Other")
        ],
        validators=[
            DataRequired()
        ]
    )

    privacy_level = SelectField(
        "Privacy",
        choices=[
            ("Family", "Family"),
            ("Admin Only", "Admin Only"),
            ("Private", "Private")
        ],
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField(
        "Upload Photo"
    )