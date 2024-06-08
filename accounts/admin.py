from django.contrib import admin

from accounts.models import User
from .models import SuperUser


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(SuperUser)
class SuperUserAdmin(admin.ModelAdmin):
    pass
