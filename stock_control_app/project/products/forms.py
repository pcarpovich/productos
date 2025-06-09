from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError
from stock_control_app.project.models import Product # For uniqueness check if needed directly

class ProductForm(FlaskForm):
    name = StringField('Product Name',
                       validators=[DataRequired(), Length(min=2, max=100)])
    unit_of_measure = StringField('Unit of Measure',
                                  validators=[Optional(), Length(max=50)]) # Made optional
    category = StringField('Category',
                           validators=[Optional(), Length(max=100)]) # Made optional
    minimum_stock = IntegerField('Minimum Stock Level',
                                 default=0,
                                 validators=[DataRequired(), NumberRange(min=0)]) # Ensure it's provided
    submit = SubmitField('Save Product')

    def validate_name(self, name):
        # Check for uniqueness if it's a new product or if name changed for an existing one
        product_id_field = self.get_product_id_field() # Helper to get ID if form has it (for edit)

        query = Product.query.filter_by(name=name.data)
        if product_id_field and product_id_field.data: # If editing and ID is present
            query = query.filter(Product.id != product_id_field.data)

        if query.first():
            raise ValidationError('This product name is already registered. Please use a different name.')

    # Helper to get product_id if it exists in the form (e.g. hidden field for edit)
    # This form doesn't explicitly have it, but WTForms-Alchemy or manual addition might add it.
    # For now, this validator works best if 'obj' is passed to the form for edits.
    def get_product_id_field(self):
        if hasattr(self, '_obj') and self._obj and hasattr(self._obj, 'id'):
            # Create a mock field to hold the ID for the validator's logic
            class MockIdField:
                def __init__(self, data):
                    self.data = data
            return MockIdField(self._obj.id)
        return None
