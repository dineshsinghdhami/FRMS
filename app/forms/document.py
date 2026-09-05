from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class DocumentForm(FlaskForm):
    title = StringField(
        "Document Title",
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

    document = FileField(
        "Document File",
        validators=[
            FileRequired(),
            FileAllowed(
                [
                    "pdf",
                    "doc",
                    "docx",
                    "xls",
                    "xlsx",
                    "jpg",
                    "jpeg",
                    "png"
                ],
                "Only PDF, Word, Excel, JPG, JPEG, and PNG files are allowed."
            )
        ]
    )

    document_type = SelectField(
        "Document Type",
        choices=[
            ("Certificate", "Certificate"),
            ("Citizenship / ID", "Citizenship / ID"),
            ("Academic", "Academic"),
            ("Property", "Property"),
            ("Insurance", "Insurance"),
            ("Legal", "Legal"),
            ("Medical", "Medical"),
            ("Financial", "Financial"),
            ("Family Record", "Family Record"),
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
        "Upload Document"
    )