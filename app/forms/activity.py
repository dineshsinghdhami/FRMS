from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class ActivityForm(FlaskForm):
    title = StringField(
        "Activity Title",
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

    activity_date = DateField(
        "Activity Date",
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
            ("Family Meeting", "Family Meeting"),
            ("Festival", "Festival"),
            ("Birthday", "Birthday"),
            ("Travel", "Travel"),
            ("Community", "Community"),
            ("Sports", "Sports"),
            ("Ceremony", "Ceremony"),
            ("Education", "Education"),
            ("Social", "Social"),
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
        "Add Activity"
    )