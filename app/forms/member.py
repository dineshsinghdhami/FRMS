from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import Email, Length, Optional, DataRequired


class FamilyMemberForm(FlaskForm):
    full_name = StringField(
        "Full Name",
        validators=[
            DataRequired(),
            Length(min=2, max=150)
        ]
    )

    date_of_birth = DateField(
        "Date of Birth",
        validators=[Optional()]
    )

    gender = SelectField(
        "Gender",
        choices=[
            ("", "Select gender"),
            ("Male", "Male"),
            ("Female", "Female"),
            ("Other", "Other")
        ],
        validators=[Optional()]
    )

    blood_group = SelectField(
        "Blood Group",
        choices=[
            ("", "Select blood group"),
            ("A+", "A+"),
            ("A-", "A-"),
            ("B+", "B+"),
            ("B-", "B-"),
            ("AB+", "AB+"),
            ("AB-", "AB-"),
            ("O+", "O+"),
            ("O-", "O-")
        ],
        validators=[Optional()]
    )

    phone = StringField(
        "Phone",
        validators=[
            Optional(),
            Length(max=30)
        ]
    )

    email = StringField(
        "Email",
        validators=[
            Optional(),
            Email(),
            Length(max=120)
        ]
    )

    permanent_address = StringField(
        "Permanent Address",
        validators=[
            Optional(),
            Length(max=255)
        ]
    )

    current_address = StringField(
        "Current Address",
        validators=[
            Optional(),
            Length(max=255)
        ]
    )

    occupation = StringField(
        "Occupation",
        validators=[
            Optional(),
            Length(max=120)
        ]
    )

    marital_status = SelectField(
        "Marital Status",
        choices=[
            ("", "Select status"),
            ("Single", "Single"),
            ("Married", "Married"),
            ("Widowed", "Widowed"),
            ("Divorced", "Divorced"),
            ("Other", "Other")
        ],
        validators=[Optional()]
    )

    emergency_contact = StringField(
        "Emergency Contact",
        validators=[
            Optional(),
            Length(max=120)
        ]
    )

    generation = IntegerField(
        "Generation",
        validators=[Optional()]
    )

    bio = TextAreaField(
        "Short Biography",
        validators=[
            Optional(),
            Length(max=2000)
        ]
    )

    submit = SubmitField("Save Family Member")