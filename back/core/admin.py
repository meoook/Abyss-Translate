from django import forms
from django.contrib import admin

from .models import Languages


class LanguageCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    name = forms.CharField(label='Name', widget=forms.TextInput)
    short_name = forms.CharField(label='Short name', widget=forms.TextInput)
    active = forms.BooleanField(label='Active', widget=forms.CheckboxInput)

    class Meta:
        model = Languages
        fields = ('name', 'short_name', 'active')

    def save(self, commit=True):
        # Save the provided password in hashed format
        lang = super().save(commit=False)
        lang.name = self.cleaned_data.get('name')
        lang.short_name = self.cleaned_data.get('short_name')
        lang.active = self.cleaned_data.get('active')
        if commit:
            lang.save()
        return lang


class LanguageChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    active = forms.BooleanField(label='Active', widget=forms.CheckboxInput)

    class Meta:
        model = Languages
        fields = ('name', 'short_name', 'active')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

@admin.register(Languages)
class LanguagesAdmin(admin.ModelAdmin):
    # The forms to add and change language instances
    form = LanguageChangeForm
    add_form = LanguageCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('name', 'short_name', 'active')
    list_filter = ('name',)
    fieldsets = (
        (None, {'fields': ('name', 'short_name', 'active')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'short_name', 'active'),
        }),
    )
    search_fields = ('name',)
    ordering = ('name',)
    filter_horizontal = ()
