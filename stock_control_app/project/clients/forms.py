from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional
# No model import needed if not doing direct uniqueness check in form for client name

class ClientForm(FlaskForm):
    name = StringField('Client Name',
                       validators=[DataRequired(), Length(min=2, max=100)])
    address = TextAreaField('Address',
                            validators=[Optional(), Length(max=250)]) # Made optional
    locality = StringField('Locality',
                           validators=[Optional(), Length(min=2, max=100)]) # Made optional
    submit = SubmitField('Save Client')
