from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """
    Custom form for creating a new user with password fields
    """

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = "Enter a strong password."
        self.fields['password2'].help_text = "Enter the same password as before, for verification."


class CustomUserChangeForm(UserChangeForm):
    """
    Custom form for updating an existing user (without password fields)
    """
    password = None  # Remove the password field from the form

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add help texts
        self.fields['username'].help_text = "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        self.fields['email'].help_text = "Optional. Enter a valid email address."
        self.fields['role'].help_text = "Select the user's role to define their permissions."
        self.fields['is_active'].help_text = "Designates whether this user account should be considered active."