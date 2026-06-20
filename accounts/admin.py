from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    list_display = ('id', 'email', 'first_name', 'last_name', 'role', 'is_approved', 'is_active')
    list_filter = ('role', 'is_approved', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'division', 'district', 'upazila', 'area')}),
        ('Permissions', {'fields': ('role', 'is_approved', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'division', 'district', 'upazila', 'area', 'role', 'is_approved', 'is_active', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('id',)
    
    
    