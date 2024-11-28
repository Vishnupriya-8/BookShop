from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
	DIVISION_CHOICES = (
		('Alappuzha', 'Alappuzha'),
		('Cherthala', 'Cherthala'),
		(' Ambalapuzha', ' Ambalapuzha'),
	)

	DISCRICT_CHOICES = (
		('Alappuzha', 'Alappuzha'), 
		('Ernakulam', 'Ernakulam'),
		('Kollam', 'Kollam'),
	)

	name = forms.CharField(max_length=30, required=True)
	email = forms.EmailField(required=True)
	phone = forms.CharField(max_length=16, required=True)
	address = forms.CharField(max_length=150, required=True)
	division = forms.ChoiceField(choices=DIVISION_CHOICES, required=True)
	district = forms.ChoiceField(choices=DISCRICT_CHOICES, required=True)
	zip_code = forms.CharField(max_length=30, required=True)

	class Meta:
		model = Order
		fields = ['name', 'email', 'phone', 'address', 'division', 'district', 'zip_code']

	def clean(self):
		cleaned_data = super().clean()
		
		# Check required fields
		required_fields = ['name', 'email', 'phone', 'address', 'division', 'district', 'zip_code']
		for field in required_fields:
			if not cleaned_data.get(field):
				self.add_error(field, f'{field.replace("_", " ").title()} is required')
		
		return cleaned_data
