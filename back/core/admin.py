# from django.contrib import admin
# from .models import Languages

# from django import forms


# @admin.register(Languages)
# class AddLanguagesAdmin(admin.ModelAdmin):
#     """A form for creating new users. Includes all the required
#     fields, plus a repeated password."""

#     name = forms.CharField(label='Name', widget=forms.TextInput)
#     short_name = forms.CharField(label='Short name', widget=forms.TextInput)
#     active = forms.BooleanField(label='Active', widget=forms.CheckboxInput)

#     class Meta:
#         model = Languages
#         fields = ('name', 'short_name', 'active')

#     def save(self, commit=True):
#         # Save the provided password in hashed format
#         language = super().save(commit=False)
#         language.set_password(self.cleaned_data["password1"])
#         if commit:
#             language.save()
#         return language


# class LanguagesAdmin(admin.ModelAdmin):
#     # The forms to add and change user instances
#     # form = UserChangeForm
#     add_form = AddLanguagesAdmin

#     # The fields to be used in displaying the User model.
#     # These override the definitions on the base UserAdmin
#     # that reference specific fields on auth.User.
#     list_display = ('name', 'short_name', 'active')
#     list_filter = ('name',)
#     fieldsets = (
#         (None, {'fields': ('name', 'short_name', 'active')}),
#     )
#     # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
#     # overrides get_fieldsets to use this attribute when creating a user.
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('name', 'short_name', 'active'),
#         }),
#     )
#     search_fields = ('name',)
#     ordering = ('name',)
#     filter_horizontal = ()
