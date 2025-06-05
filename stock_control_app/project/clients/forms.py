from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

class ClientForm(FlaskForm):
    name = StringField('Client Name',
                       validators=[DataRequired(), Length(min=2, max=100)])
    address = TextAreaField('Address',
                            validators=[DataRequired(), Length(max=250)]) # Using TextAreaField for potentially longer addresses
    locality = StringField('Locality',
                           validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Save Client')
