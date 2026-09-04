from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired


class RelationshipForm(FlaskForm):
    related_member_id = SelectField(
        "Related Family Member",
        coerce=int,
        validators=[DataRequired()]
    )

    relationship_type = SelectField(
        "Relationship",
        choices=[
            ("Father", "Father"),
            ("Mother", "Mother"),
            ("Husband", "Husband"),
            ("Wife", "Wife"),
            ("Spouse", "Spouse"),
            ("Son", "Son"),
            ("Daughter", "Daughter"),
            ("Brother", "Brother"),
            ("Sister", "Sister"),
            ("Grandfather", "Grandfather"),
            ("Grandmother", "Grandmother"),
            ("Grandchild", "Grandchild"),
            ("Uncle", "Uncle"),
            ("Aunt", "Aunt"),
            ("Cousin", "Cousin"),
            ("Other", "Other")
        ],
        validators=[DataRequired()]
    )

    submit = SubmitField("Add Relationship")