from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class ProductForm(FlaskForm):
    name = StringField('Product Name',
                       validators=[DataRequired(), Length(min=2, max=100)])
    unit_of_measure = StringField('Unit of Measure',
                                  validators=[Length(max=50)])
    category = StringField('Category',
                           validators=[Length(max=100)])
    minimum_stock = IntegerField('Minimum Stock Level',
                                 default=0,
                                 validators=[NumberRange(min=0)])
    submit = SubmitField('Save Product')
