from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean(self):
        # Get the cleaned data
        print("clean")
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            # Authenticate the user
            user = authenticate(username=username, password=password)
            
            if user is None:
                # If authentication fails, add an error to the form
                raise ValidationError("Invalid username or password.")
            
            # Optionally, you could add extra validation here if needed (e.g., account is active)
        
        return cleaned_data