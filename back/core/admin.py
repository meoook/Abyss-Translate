from django.contrib import admin
from .models import Languages, Translates


# Register your models here.
class LanguagesAdmin(admin.ModelAdmin):
    pass


admin.site.register(Languages)
admin.site.register(Translates)
