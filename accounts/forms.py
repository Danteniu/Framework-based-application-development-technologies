from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User, UserRole


class RegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=UserRole.choices, label="Роль")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role")


