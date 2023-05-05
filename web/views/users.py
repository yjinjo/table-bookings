import os
from datetime import timedelta

from allauth.socialaccount.models import SocialAccount
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import FormView, UpdateView
from dotenv import load_dotenv

from web.forms import RegisterForm, LoginForm, ProfileForm, PasswordForm
from web.models import UserProfile, UserVerification
from web.utils import create_email_key

load_dotenv()


def send_verification_mail(request, user, receiver):
    key = create_email_key(user.id)
    link = "http://" + request.get_host() + reverse("verification") + "?key=" + key

    expired_at = timezone.now() + timedelta(days=3)
    UserVerification.objects.create(user=user, key=key, expired_at=expired_at)

    email_context = {"link": link}
    msg_plain = render_to_string("email/verification.txt", email_context)
    msg_html = render_to_string("email/verification.html", email_context)
    send_mail(
        "이메일 인증을 완료해주세요.",
        msg_plain,
        os.environ.get("SENDER_EMAIL"),
        [receiver],
        html_message=msg_html,
        fail_silently=True,
    )


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

        send_verification_mail(self.request, user, email)

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


class VerificationView(View):
    """이메일이 발송되고 나서 이메일 안에 있는 링크가 클릭되었을 때 key를 받아서
    DB에서 검증처리"""

    def get(self, request):
        key = request.GET.get("key", "")
        verification = UserVerification.objects.get(key=key)
        current = timezone.now()

        if verification.expired_at > current:
            verification.verified = True
            verification.verified_at = current
            verification.save()

            user = verification.user
            user.userprofile.verified = True
            user.save()

            messages.success(self.request, "인증이 완료되었습니다.")
        else:
            messages.warning(self.request, "인증을 다시 시도해주세요.")

        return redirect(reverse("index"))


class ProfileView(UpdateView):
    form_class = ProfileForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return UserProfile.objects.get(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        social_account = SocialAccount.objects.filter(user=self.request.user).first()
        context["is_social_login"] = social_account is not None
        return context


class PasswordView(FormView):
    template_name = "users/password.html"
    form_class = PasswordForm
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        old_password = form.cleaned_data.get("old_password")
        password = form.cleaned_data.get("new_password")
        password_confirm = form.cleaned_data.get("confirm_password")

        if password != password_confirm:
            messages.warning(self.request, "2개의 비밀번호가 일치하지 않습니다.")
            return redirect(reverse("password"))
        elif not self.request.user.check_password(old_password):
            messages.warning(self.request, "기존 비밀번호가 일치하지 않습니다.")
            return redirect(reverse("password"))
        else:
            self.request.user.set_password(password)
            self.request.user.save()
            messages.warning(self.request, "비밀번호가 수정되었습니다.")
            return super().form_valid(form)
