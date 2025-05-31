from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages

from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'users/login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


@method_decorator(login_required, name='dispatch')
class UserListView(UserPassesTestMixin, ListView):
    """List all users - accessible only to admins"""
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'

    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_superuser


@method_decorator(login_required, name='dispatch')
class UserCreateView(UserPassesTestMixin, CreateView):
    """Create a new user - accessible only to admins"""
    model = User
    template_name = 'users/user_form.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('user-list')

    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, f"User {form.cleaned_data['username']} created successfully")
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UserPassesTestMixin, UpdateView):
    """Update existing user - accessible only to admins"""
    model = User
    template_name = 'users/user_form.html'
    form_class = CustomUserChangeForm
    success_url = reverse_lazy('user-list')

    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, f"User {form.instance.username} updated successfully")
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class UserDeleteView(UserPassesTestMixin, DeleteView):
    """Delete existing user - accessible only to admins"""
    model = User
    template_name = 'users/user_confirm_delete.html'
    success_url = reverse_lazy('user-list')

    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_superuser

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        messages.success(request, f"User {user.username} deleted successfully")
        return super().delete(request, *args, **kwargs)


@login_required
def profile_view(request):
    """View for users to see their own profile"""
    return render(request, 'users/profile.html')