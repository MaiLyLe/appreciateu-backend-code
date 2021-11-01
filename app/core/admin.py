from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
from core import models


class UserAdmin(BaseUserAdmin):
    """Configuration for user model in Django admin panel"""
    ordering = ['id']
    list_display = ['email', 'name', 'id', 'avatar_num']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'is_student',
                    'is_professor',
                    'google_email',
                    'google_last_updated',
                    'entry_semester'
                    'avatar_num',
                    'user_image'
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        })
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Student)
admin.site.register(models.Professor)
admin.site.register(models.FieldOfStudies)
admin.site.register(models.Institute)
admin.site.register(models.Course)
admin.site.register(models.GoogleContact)


@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    """Custom configuration for message model in Django admin panel"""
    list_display = ('pk', 'text', 'timestamp', 'is_seen', 'sender', 'receiver')
