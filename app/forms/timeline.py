from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class TimelineEventForm(FlaskForm):
    title = StringField(
        "Title",
        validators=[
            DataRequired(),
            Length(min=2, max=150)
        ]
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(max=3000)
        ]
    )

    event_date = DateField(
        "Event Date",
        validators=[Optional()]
    )

    year = IntegerField(
        "Year",
        validators=[
            Optional(),
            NumberRange(min=1900, max=2200)
        ]
    )

    category = SelectField(
        "Category",
        choices=[
            ("Birth", "Birth"),
            ("Education", "Education"),
            ("Career", "Career"),
            ("Marriage", "Marriage"),
            ("Family", "Family"),
            ("Travel", "Travel"),
            ("Achievement", "Achievement"),
            ("Training", "Training"),
            ("Project", "Project"),
            ("Community", "Community"),
            ("Personal Milestone", "Personal Milestone"),
            ("Other", "Other")
        ],
        validators=[DataRequired()]
    )

    location = StringField(
        "Location",
        validators=[
            Optional(),
            Length(max=150)
        ]
    )

    privacy_level = SelectField(
        "Privacy",
        choices=[
            ("Family", "Family"),
            ("Admin Only", "Admin Only"),
            ("Private", "Private")
        ],
        validators=[DataRequired()]
    )

    submit = SubmitField("Add Timeline Event")