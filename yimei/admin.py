from django.contrib import admin
from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ["get_full_name", "tele", "email"]
    search_fields = ["get_full_name", "tele", "email"]
    list_per_page = 10
    fieldsets = (
        ("基本信息", {
            "fields": (("last_name", "first_name"), "tele", "email", "nick", "loca")
        }),
        ("高级", {
            "fields": ("username", "password", "last_login","date_joined", "is_active")
        }),
        ("权限管理", {
            "fields": ("groups", "user_permissions", "is_staff", "is_superuser")
        })
    )


class LocationAdmin(admin.ModelAdmin):
    search_fields = ("code", "name", )
    list_per_page = 10


admin.site.register(Location, LocationAdmin)
admin.site.register(User_Profile, UserAdmin)
