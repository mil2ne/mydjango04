from django.contrib import admin

from accounts.models import User
from .models import SuperUser, Profile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(SuperUser)
class SuperUserAdmin(admin.ModelAdmin):
    pass


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass
