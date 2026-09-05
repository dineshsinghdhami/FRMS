from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class AnnouncementForm(FlaskForm):
    title = StringField(
        "Announcement Title",
        validators=[
            DataRequired(),
            Length(max=150)
        ]
    )

    message = TextAreaField(
        "Message",
        validators=[
            DataRequired(),
            Length(max=3000)
        ]
    )

    category = SelectField(
        "Category",
        choices=[
            ("General", "General"),
            ("Family Update", "Family Update"),
            ("Reminder", "Reminder"),
            ("Invitation", "Invitation"),
            ("Emergency", "Emergency"),
            ("Meeting", "Meeting"),
            ("Document", "Document"),
            ("Festival", "Festival"),
            ("Other", "Other")
        ],
        validators=[
            DataRequired()
        ]
    )

    priority = SelectField(
        "Priority",
        choices=[
            ("Low", "Low"),
            ("Normal", "Normal"),
            ("High", "High"),
            ("Urgent", "Urgent")
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
        "Add Announcement"
    )