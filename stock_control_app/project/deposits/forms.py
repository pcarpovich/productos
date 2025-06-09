from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from stock_control_app.project.models import Deposit # For uniqueness check

class DepositForm(FlaskForm):
    name = StringField('Deposit Name',
                       validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Save Deposit')

    def validate_name(self, name):
        # Helper to get deposit_id if it exists in the form (e.g. hidden field for edit)
        deposit_id_val = None
        if hasattr(self, '_obj') and self._obj and hasattr(self._obj, 'id'):
            deposit_id_val = self._obj.id

        query = Deposit.query.filter_by(name=name.data)
        if deposit_id_val: # If editing and ID is present
            query = query.filter(Deposit.id != deposit_id_val)

        if query.first():
            raise ValidationError('This deposit name is already registered. Please use a different name.')
