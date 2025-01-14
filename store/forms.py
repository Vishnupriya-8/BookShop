from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from .models import Review

class RegistrationForm(UserCreationForm):
    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = [
            'name',
            'email',
            'username',
            'password1',
            'password2'
        ]
    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data['name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                attrs={'class': 'form-control'},
                choices=[(i, f'{i} Stars') for i in range(1, 6)]
            ),
            'comment': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your review here...'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False

    