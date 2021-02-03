from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from tsuser.models import TesseloUser

admin.site.register(TesseloUser, UserAdmin)
