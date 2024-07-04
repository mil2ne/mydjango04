from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect
from formtools.wizard.views import SessionWizardView
from vanilla import UpdateView, CreateView

from accounts.forms import ProfileForm, UserForm, UserProfileForm, SignupForm
from accounts.models import Profile
from mysite import settings


# @login_required
# def profile_edit(request):
#     try:
#         instance = request.user.profile
#     except Profile.DoesNotExist:
#         instance = None
#
#     if request.method == "GET":
#         form = ProfileForm(instance=instance)
#     else:
#         form = ProfileForm(data=request.POST, files=request.FILES, instance=instance)
#         if form.is_valid():
#             profile = form.save(commit=False)
#             profile.user = request.user
#             profile.save()
#             return redirect("accounts:profile_edit")
#     return render(
#         request,
#         "accounts/profile_form.html",
#         {"form": form},
#     )


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    success_url = reverse_lazy("accounts:profile_edit")

    def get_object(self):
        try:
            return self.request.user.profile
        except Profile.DoesNotExist:
            return None

    def form_valid(self, form):
        profile = form.save(commit=False)
        profile.user = self.request.user
        return super().form_valid(form)


profile_edit = ProfileUpdateView.as_view()


def check_is_profile_update(wizard_view: "UserProfileWizardView") -> bool:
    cleaned_data = wizard_view.get_cleaned_data_for_step("user_form")
    if cleaned_data is None:
        return True
    return cleaned_data.get("is_profile_update", False)


class UserProfileWizardView(LoginRequiredMixin, SessionWizardView):
    form_list = [("user_form", UserForm), ("profile_form", UserProfileForm)]
    template_name = "accounts/profile_wizard.html"
    file_storage = default_storage

    condition_dict = {
        "profile_form": check_is_profile_update,
    }

    def get_form_instance(self, step):
        if step == "user_form":
            return self.request.user
        elif step == "profile_form":
            profile, __ = Profile.objects.get_or_create(user=self.request.user)
            return profile
        return super().get_form_instance(step)

    def done(self, form_list, form_dict, **kwargs):  # noqa
        # for form in form_list:
        #     form.save()

        # form_list[0].save()
        # form_list[1].save()

        user = form_dict["user_form"].save()

        if "profile_form" in form_dict:
            profile = form_dict["profile_form"].save(commit=False)
            profile.user = user
            profile.save()

        messages.success(self.request, "프로필을 저장했습니다.")
        return redirect("accounts:profile_wizard")


profile_wizard = UserProfileWizardView.as_view()


# def login(request):
#     if request.method == "GET":
#         return render(request, "accounts/login_form.html")
#     else:
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#
#         # authenticate 함수를 통해 유저명/암호를 검증할 수 있습니다.
#         #   - 인증에 성공하면 관련 User 모델 인스턴스를 반환하며, 실패하면 None을 반환
#         #   - auth 앱의 AuthenticationForm 에서 사용합니다.
#         user = authenticate(request, username=username, password=password)
#         if user is None:
#             return HttpResponse("인증 실패", status=400)
#
#         if user.is_active is False:
#             return HttpResponse("비활성화된 계정입니다.", status=400)
#
#         # 유저명/암호로 검증이 되면, auth 앱의 login 함수에서 로그인 과정을 처리해줍니다.
#
#         # 1) 아래 login 함수만 호출하면, 세션을 이용한 로그인 과정 끝.
#         #   - 세션 키를 생성하고, 세션에 아래 3개 정보를 남기고, CSRF 토큰도 재생성합니다.
#         #   - User 모델의 .last_login 필드를 현재 시각으로 업데이트합니다.
#         # auth_login(request, user)
#
#         # 2) 혹은 세션 저장 부분만 직접 구현해본다면, 아래와 같습니다.
#         #   - 인증에 사용된 백엔드가 .backend 속성에 저장되어있습니다.
#         request.session["_auth_user_backend"] = user.backend
#         request.session["_auth_user_id"] = user.pk
#         request.session["_auth_user_hash"] = user.get_session_auth_hash()
#
#         # 로그인 성공 페이지로 이동하기
#         #  디폴트 주소로 settings.LOGIN_REDIRECT_URL (디폴트: "/accounts/profile/")
#         next_url = (
#             request.POST.get("next")
#             or request.GET.get("next")
#             or settings.LOGIN_REDIRECT_URL
#         )
#         return redirect(next_url)


class LoginView(DjangoLoginView):
    template_name = "accounts/login_form.html"
    # redirect_authenticated_user = True


login = LoginView.as_view()


def profile(request):
    return HttpResponse(
        f"username : {request.user.username} , {request.user.is_authenticated}"
    )


# def signup(request):
#     if request.method == "GET":
#         form = SignupForm()
#     else:
#         form = SignupForm(data=request.POST)
#         if form.is_valid():
#             create_user = form.save()
#             auth_login(request, create_user)
#             # return redirect(settings.LOGIN_URL)
#             return redirect(settings.LOGIN_REDIRECT_URL)
#     return render(request, "accounts/signup_form.html", {"form": form})


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup_form.html"
    success_url = settings.LOGIN_REDIRECT_URL

    def form_valid(self, form):
        response = super().form_valid(form)
        create_user = form.instance
        auth_login(self.request, create_user)
        return response


signup = SignupView.as_view()
