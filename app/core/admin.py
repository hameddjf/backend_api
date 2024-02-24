"""
django admin customization.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from core import models


class UserAdmin(UserAdmin):
    """define the admin pages for users."""
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {
            "fields": (
                'email',
                'password',
            ),
        }),

        (_('دسترسی ها'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
            ),
        }),
        (_('تاریخ های مهم'), {
            'fields': (
                'last_login',
            )
        }),
    )
    readonly_fields = ['last_login']
    # add new user
    add_fieldsets = (
        (None, {
            # مرتب میکنه بصورت عریض
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )


admin.site.register(models.User, UserAdmin)
