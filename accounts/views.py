from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from accounts.forms import ProfileForm
from accounts.models import Profile


@login_required
def profile_edit(request):
    try:
        instance = request.user.profile
    except Profile.DoesNotExist:
        instance = None

    if request.method == "GET":
        form = ProfileForm(instance=instance)
    else:
        form = ProfileForm(data=request.POST, files=request.FILES, instance=instance)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect("accounts:profile_edit")
    return render(
        request,
        "accounts/profile_form.html",
        {"form": form},
    )
