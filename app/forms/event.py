from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, SubmitField, TextAreaField, TimeField
from wtforms.validators import DataRequired, Length, Optional


class EventForm(FlaskForm):
    title = StringField(
        "Event Title",
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

    event_date = DateField(
        "Event Date",
        validators=[
            DataRequired()
        ]
    )

    event_time = TimeField(
        "Event Time",
        validators=[
            Optional()
        ]
    )

    location = StringField(
        "Location",
        validators=[
            Optional(),
            Length(max=200)
        ]
    )

    category = SelectField(
        "Category",
        choices=[
            ("Birthday", "Birthday"),
            ("Wedding", "Wedding"),
            ("Anniversary", "Anniversary"),
            ("Family Gathering", "Family Gathering"),
            ("Festival", "Festival"),
            ("Ceremony", "Ceremony"),
            ("Meeting", "Meeting"),
            ("Trip", "Trip"),
            ("Religious", "Religious"),
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
        "Add Event"
    )