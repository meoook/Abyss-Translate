from django.contrib import admin
from .models import Languages

# Register your models here.
class LanguagesAdmin(admin.ModelAdmin):
    pass
admin.site.register(Languages)
