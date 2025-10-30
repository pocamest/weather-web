from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views import View

from .forms import LoginForm, RegistrationForm


class RegistrationView(View):
    form_class = RegistrationForm
    template_name = 'users/registration.html'

    def get(self, request: HttpRequest) -> HttpResponse:
        form = self.form_class()
        return render(
            request=request, template_name=self.template_name, context={'form': form}
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect(settings.REGISTRATION_REDIRECT_URL)
        return render(
            request=request, template_name=self.template_name, context={'form': form}
        )


class LoginView(View):
    form_class = LoginForm
    template_name = 'users/login.html'

    def get(self, request: HttpRequest) -> HttpResponse:
        form = self.form_class()
        return render(
            request=request, template_name=self.template_name, context={'form': form}
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        form = self.form_class(request.POST)
        if form.is_valid():
            login_identifier = form.cleaned_data['login_identifier']
            password = form.cleaned_data['password']
            user = authenticate(
                request=request, username=login_identifier, password=password
            )
            if user is not None:
                login(request=request, user=user)
                return redirect(settings.LOGIN_REDIRECT_URL)
            else:
                form.add_error(None, 'Invalid username/email or password.')
        return render(
            request=request, template_name=self.template_name, context={'form': form}
        )


class LogoutView(View):
    def post(self, request: HttpRequest) -> HttpResponse:
        logout(request)
        return redirect(settings.LOGOUT_REDIRECT_URL)
