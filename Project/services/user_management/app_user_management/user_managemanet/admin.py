from django.contrib import admin
from . import  models

# Register your models here.
# @admin.register(models.CustomUser)
# @admin.register(models.Friendship)


admin.site.register(models.CustomUser)
admin.site.register(models.Friendship)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name') 
