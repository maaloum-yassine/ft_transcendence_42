from django.contrib import admin
from .models import Message
from .models import Connected

admin.site.register(Message)
admin.site.register(Connected)
# Register your models here.
