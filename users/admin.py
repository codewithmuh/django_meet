from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from users.models import ApiKey, UserSignupCode
from users.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext, gettext_lazy as _

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email',
                                         "dob", "gender",
                                         "image", "nationality", "passport_no", "email_confirmed")}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'), #  'groups', 'user_permissions'
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ['email', "first_name", "last_name", 'dob', 'gender', "passport_no", "nationality", "is_superuser",  'email_confirmed']
    search_fields = ["name", "nationality", "passport_no", "email"]


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('api_key', "created")


@admin.register(UserSignupCode)
class UserSignupCodeAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', "created")
