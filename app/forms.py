from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import *

class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ProfileUpdateForm(forms.ModelForm):
    user_image = models.ImageField(upload_to="photo/%Y/%m/%d/")
    description = models.TextField(blank=True)

    class Meta:
        model = Profile
        fields = ['user_image', 'description']


