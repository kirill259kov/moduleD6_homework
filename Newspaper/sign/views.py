from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from .forms import LoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView
from .forms import RegisterForm
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.template.loader import render_to_string


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'sign/signup.html'
    success_url = '/'

    def form_valid(self, form):
        user = form.save()
        group = Group.objects.get_or_create(name='common')[0]
        user.groups.add(group)
        user.save()
        return super().form_valid(form)


class LoginView(FormView):
    model = User
    form_class = LoginForm
    template_name = 'sign/login.html'
    success_url = '/'

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)


class LogoutView(LoginRequiredMixin, TemplateView):
    template_name = 'sign/logout.html'

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)