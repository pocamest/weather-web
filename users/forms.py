from typing import TYPE_CHECKING, Any

from django import forms
from django.contrib.auth import get_user_model

if TYPE_CHECKING:
    from .models import User

UserModel: type[User] = get_user_model()


class RegistrationForm(forms.Form):
    username = forms.CharField(label='Username', max_length=150)
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    def clean_username(self) -> str:
        username: str = self.cleaned_data['username']
        normalize_username = username.strip().lower()
        if UserModel.objects.filter(username=normalize_username).exists():
            raise forms.ValidationError('A user with that username already exists')
        return normalize_username

    def clean_email(self) -> str:
        email: str = self.cleaned_data['email']
        normalize_email = email.strip().lower()
        if UserModel.objects.filter(email=normalize_email).exists():
            raise forms.ValidationError('A user with that email already exists')
        return normalize_email

    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()
        if cleaned_data:
            password1 = cleaned_data.get('password1')
            password2 = cleaned_data.get('password2')
            if password1 and password2 and password1 != password2:
                raise forms.ValidationError("Passwords don't match")
        return cleaned_data

    def save(self) -> User:
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password1']
        return UserModel.objects.create_user(
            username=username, email=email, password=password
        )
