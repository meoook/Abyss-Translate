# from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Languages, Files, Folders, FileMarks, Translates


class MarkInline(admin.TabularInline):
    model = FileMarks
    extra = 0

    fields = 'id', 'mark_number', 'col_number', 'md5sum', 'md5sum_clear', 'words'
    read_only_fields = 'mark_number', 'col_number', 'md5sum', 'md5sum_clear', 'words'
    # template = 'admin/sortable_tabular_inline.html'

    # def preview(self, obj):
    #     return get_tabular_photo_preview(obj.image)
    

@admin.register(Files)
class FilesAdmin(admin.ModelAdmin):
    prepopulated_fields = {'method': ('name',)}
    list_display = ['id', 'name', 'state', 'method', 'items', 'words', 'lang_orig', 'translated_set', 'created', 'updated', 'repo_status', 'repo_hash', 'get_thumb']
    list_display_links = ['name']
    list_filter = ['state', 'repo_status', 'method']
    read_only_fields = ['state', 'method', 'items', 'words', 'created', 'updated', 'repo_status', 'repo_hash']
    list_editable = ['lang_orig']
    search_fields = ['name']

    fieldsets = (
        (None, {'fields': ('id', 'name', 'state', 'method', 'items', 'words')}),
        (None, {'fields': ('lang_orig', 'translated_set')}),
        (None, {'classes': ('collapse',), 'fields': ('repo_status', 'repo_hash'), }),
    )

    save_on_top = True      # Menu for save on top

    inlines = (MarkInline, )

    def get_thumb(self, obj):
        return mark_safe(f'<small>{obj.get_method_display}</small>')
    get_thumb.short_description = u'Тут что то будет'


@admin.register(FileMarks)
class FileMarksAdmin(admin.ModelAdmin):
    list_display = ['id', 'file', 'mark_number', 'col_number']


@admin.register(Translates)
class TranslatesAdmin(admin.ModelAdmin):
    list_display = ['id', 'mark_id', 'text']


@admin.register(Languages)
class LanguagesAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'short_name', 'active']

# class LanguageCreationForm(forms.ModelForm):
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
#         lang = super().save(commit=False)
#         lang.name = self.cleaned_data.get('name')
#         lang.short_name = self.cleaned_data.get('short_name')
#         lang.active = self.cleaned_data.get('active')
#         if commit:
#             lang.save()
#         return lang


# class LanguageChangeForm(forms.ModelForm):
#     """A form for updating users. Includes all the fields on
#     the user, but replaces the password field with admin's
#     password hash display field.
#     """
#     active = forms.BooleanField(label='Active', widget=forms.CheckboxInput)

#     class Meta:
#         model = Languages
#         fields = ('name', 'short_name', 'active')

#     def clean_password(self):
#         # Regardless of what the user provides, return the initial value.
#         # This is done here, rather than on the field, because the
#         # field does not have access to the initial value
#         return self.initial["password"]


# @admin.register(Languages)
# class LanguagesAdmin(admin.ModelAdmin):
#     # The forms to add and change language instances
#     form = LanguageChangeForm
#     add_form = LanguageCreationForm

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


