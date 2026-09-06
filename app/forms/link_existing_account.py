from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired


class LinkExistingAccountForm(FlaskForm):
    member_id = SelectField(
        "Family Member",
        coerce=int,
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField(
        "Link Account"
    )