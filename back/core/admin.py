# from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Language, File, Folder, FileMark, Translate, FolderRepo


class MarkInline(admin.TabularInline):
    model = FileMark
    extra = 0

    fields = 'id', 'fid', 'search_words'
    read_only_fields = 'fid', 'search_words'
    # template = 'admin/sortable_tabular_inline.html'

    # def preview(self, obj):
    #     return get_tabular_photo_preview(obj.image)


@admin.register(File)
class FilesAdmin(admin.ModelAdmin):
    prepopulated_fields = {'method': ('name',)}
    list_display = ['id', 'name', 'method', 'items', 'words', 'lang_orig', 'translated_set', 'created', 'updated', 'repo_status', 'repo_sha', 'get_thumb']
    list_display_links = ['name']
    list_filter = ['repo_status', 'method']
    read_only_fields = ['method', 'items', 'words', 'created', 'updated', 'repo_status', 'repo_sha']
    list_editable = ['lang_orig']
    search_fields = ['name']

    fieldsets = (
        (None, {'fields': ('id', 'name', 'method', 'items', 'words')}),
        (None, {'fields': ('lang_orig', 'translated_set')}),
        (None, {'classes': ('collapse',), 'fields': ('repo_status', 'repo_sha'), }),
    )

    save_on_top = True      # Menu for save on top

    inlines = (MarkInline, )

    def get_thumb(self, obj):
        return mark_safe(f'<small>{obj.get_method_display}</small>')
    get_thumb.short_description = u'Тут что то будет'


@admin.register(FileMark)
class FileMarksAdmin(admin.ModelAdmin):
    list_display = ['id', 'file', 'fid']


@admin.register(Translate)
class TranslatesAdmin(admin.ModelAdmin):
    list_display = ['id', 'item_id', 'text']


@admin.register(Language)
class LanguagesAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'short_name', 'active']


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'repo_url', 'repo_status']


@admin.register(FolderRepo)
class FolderRepoAdmin(admin.ModelAdmin):
    list_display = ['folder_id', 'provider', 'owner', 'name', 'branch', 'path', 'access']


# class LanguageCreationForm(forms.ModelForm):
#     """A form for creating new users. Includes all the required
#     fields, plus a repeated password."""

#     name = forms.CharField(label='Name', widget=forms.TextInput)
#     short_name = forms.CharField(label='Short name', widget=forms.TextInput)
#     active = forms.BooleanField(label='Active', widget=forms.CheckboxInput)

#     class Meta:
#         model = Language
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
#     the user, but replaces the password field with admin
#     password hash display field.
#     """
#     active = forms.BooleanField(label='Active', widget=forms.CheckboxInput)

#     class Meta:
#         model = Language
#         fields = ('name', 'short_name', 'active')

#     def clean_password(self):
#         # Regardless of what the user provides, return the initial value.
#         # This is done here, rather than on the field, because the
#         # field does not have access to the initial value
#         return self.initial["password"]


# @admin.register(Language)
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
