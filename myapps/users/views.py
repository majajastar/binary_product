from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .forms import SignupForm, LoginForm
from django.contrib import messages

def signup(request):
    if request.user.is_authenticated:
        # If the user is already logged in, redirect to the home page
        return redirect('home')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after signup
            return redirect('home')  # Redirect to a page (e.g., home) after signup
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        # If the user is already logged in, redirect to the home page
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(data = request.POST)
        if form.is_valid():
            # Authentication is already handled in the form's clean method
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to home or another page after successful login
            else:
                # In case authentication fails even after form validation, add a general error message
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Form is invalid. Please check the input.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to home after logout