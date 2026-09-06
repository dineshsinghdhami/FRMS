from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class FamilyHistoryForm(FlaskForm):
    title = StringField(
        "History Title",
        validators=[
            DataRequired(),
            Length(max=150)
        ]
    )

    description = TextAreaField(
        "Description",
        validators=[
            DataRequired(),
            Length(max=5000)
        ]
    )

    year = IntegerField(
        "Year",
        validators=[
            Optional(),
            NumberRange(
                min=1000,
                max=2200,
                message="Enter a valid year."
            )
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
            ("Family Origin", "Family Origin"),
            ("Migration", "Migration"),
            ("Ancestral Story", "Ancestral Story"),
            ("Major Milestone", "Major Milestone"),
            ("Property History", "Property History"),
            ("Education", "Education"),
            ("Career", "Career"),
            ("Community", "Community"),
            ("Tradition", "Tradition"),
            ("Achievement", "Achievement"),
            ("General", "General"),
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
        "Add History Record"
    )