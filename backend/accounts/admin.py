from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Qo‘shimcha ma’lumotlar', {'fields': ('role', 'phone', 'subject')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Qo‘shimcha ma’lumotlar', {'fields': ('role', 'first_name', 'last_name', 'phone', 'subject', 'email')}),
    )
    list_display = ('username', 'first_name', 'last_name', 'role', 'phone', 'subject', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'phone', 'subject')
