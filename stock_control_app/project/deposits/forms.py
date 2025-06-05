from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class DepositForm(FlaskForm):
    name = StringField('Deposit Name',
                       validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Save Deposit')
