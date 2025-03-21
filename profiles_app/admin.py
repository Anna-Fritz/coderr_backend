from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import BusinessProfile, CustomerProfile, CustomUser

# Register your models here.


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'type']
    list_filter = ['is_staff', 'is_active', 'type']
    search_fields = ['username', 'email']
    ordering = ['username']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Custom Fields', {'fields': ('type',)}),  # Hier fügen wir das `type`-Feld hinzu
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'type'),
        }),
    )


admin.site.register([BusinessProfile, CustomerProfile])
admin.site.register(CustomUser, CustomUserAdmin)