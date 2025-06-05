from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp
from wtforms import ValidationError
from stock_control_app.project.models import Operator # For uniqueness check

class OperatorForm(FlaskForm):
    name = StringField('Operator Name',
                       validators=[DataRequired(), Length(min=2, max=100)])
    dni = StringField('DNI/ID',
                      validators=[DataRequired(),
                                  Length(min=3, max=20),
                                  Regexp(r'^[a-zA-Z0-9\-\.]*$',
                                         message="DNI can only contain letters, numbers, hyphens, and dots.")
                                 ]
                     )
    submit = SubmitField('Save Operator')

    def validate_dni(self, dni):
        # Check for uniqueness if it's a new operator or if DNI changed for an existing one
        operator_id = None
        if hasattr(self, '_obj') and self._obj: # _obj is often passed by WTForms-Alchemy or when pre-populating
            operator_id = self._obj.id

        query = Operator.query.filter_by(dni=dni.data)
        if operator_id:
            query = query.filter(Operator.id != operator_id)

        if query.first():
            raise ValidationError('This DNI is already registered. Please use a different DNI.')
