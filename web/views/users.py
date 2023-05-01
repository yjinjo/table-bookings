from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import FormView

from web.forms import RegisterForm, LoginForm
from web.models import UserProfile


class RegisterView(FormView):
    template_name = "users/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        nickname = form.cleaned_data["nickname"]
        profile_image = form.cleaned_data["profile_image"]

        user = User.objects.create_user(email, email, password)
        UserProfile.objects.create(
            user=user, nickname=nickname, profile_image=profile_image
        )

        return super().form_valid(form)


class LoginView(FormView):
    template_name = "users/login.html"
    success_url = reverse_lazy("index")
    form_class = LoginForm

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        user = auth.authenticate(username=email, password=password)

        if user:
            auth.login(self.request, user)
            return super().form_valid(form)
        else:
            messages.warning(self.request, "계정 혹은 비밀번호를 확인해주세요.")
            return redirect(reverse("login"))


class LogoutView(View):
    def get(self, request):
        auth.logout(request)
        return redirect(reverse("index"))
