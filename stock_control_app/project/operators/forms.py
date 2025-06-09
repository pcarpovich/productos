from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError, Optional
from stock_control_app.project.models import Operator # For uniqueness check

class OperatorForm(FlaskForm):
    name = StringField('Operator Name',
                       validators=[DataRequired(), Length(min=2, max=100)])
    dni = StringField('DNI/ID',
                      validators=[DataRequired(),
                                  Length(min=3, max=20),
                                  Regexp(r'^[a-zA-Z0-9\-\.\s]*$', # Allow spaces too
                                         message="DNI can only contain letters, numbers, hyphens, dots, and spaces.")
                                 ]
                     )
    submit = SubmitField('Save Operator')

    def validate_dni(self, dni):
        operator_id_val = None
        if hasattr(self, '_obj') and self._obj and hasattr(self._obj, 'id'):
            operator_id_val = self._obj.id

        query = Operator.query.filter_by(dni=dni.data)
        if operator_id_val:
            query = query.filter(Operator.id != operator_id_val)

        if query.first():
            raise ValidationError('This DNI is already registered. Please use a different DNI.')
