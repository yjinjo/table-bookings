from django import forms
from django.utils.translation import gettext_lazy as _

from web.models import UserProfile


class RegisterForm(forms.Form):
    email = forms.EmailField(
        label="이메일",
        error_messages={"invalid": "유효한 이메일 주소를 입력해주세요."},
    )
    password = forms.CharField(
        label="비밀번호",
        min_length=6,
        max_length=20,
        widget=forms.PasswordInput,
    )
    password_confirm = forms.CharField(
        label="비밀번호 확인",
        min_length=6,
        max_length=20,
        widget=forms.PasswordInput,
    )
    nickname = forms.CharField(
        label="닉네임",
        min_length=2,
        max_length=10,
    )
    profile_image = forms.ImageField(
        label="프로필 사진",
        required=False,
    )

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError(
                    {"password_confirm": ["2개의 비밀번호가 일치하지 않습니다."]}
                )

        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="이메일",
        error_messages={"invalid": "유효한 이메일 주소를 입력해주세요."},
    )
    password = forms.CharField(
        label="비밀번호",
        min_length=6,
        max_length=20,
        widget=forms.PasswordInput,
    )


class ProfileImageFileInput(forms.ClearableFileInput):
    """기존의 이미지 필드의 라벨링을 바꿉니다. Default는 영어로 뜨는데 그것을 한글화함"""

    initial_text = _("기존 이미지")
    input_text = _("변경할 이미지")
    clear_checkbox_label = _("이미지 삭제")


class ProfileForm(forms.ModelForm):
    profile_image = forms.ImageField(
        label=_("선택된 이미지"),
        required=False,
        widget=ProfileImageFileInput,
    )

    class Meta:
        model = UserProfile
        fields = (
            "nickname",
            "profile_image",
        )
        labels = {
            "nickname": _("닉네임"),
            "profile_image": _("프로필 이미지"),
        }


class PasswordForm(forms.Form):
    """우선은 검증없이 간단하게 작성 TODO"""

    old_password = forms.CharField(
        widget=forms.PasswordInput(),
        min_length=6,
        max_length=16,
        label=_("기존 비밀번호"),
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(),
        min_length=6,
        max_length=16,
        label=_("새 비밀번호"),
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(),
        min_length=6,
        max_length=16,
        label=_("새 비밀번호 확인"),
    )
