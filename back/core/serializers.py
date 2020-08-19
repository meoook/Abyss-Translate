from rest_framework import serializers
from rest_framework.exceptions import APIException

from .models import Projects, Folders, Languages, Files, ErrorFiles, Translates, FileMarks, Translated

# Extra kwargs write_only, read_only, required, default, allow_null, label
# source -> The name of the attribute that will be used to populate the field : URLField(source='get_absolute_url')
# validators - > A list of validator functions which should be applied to the incoming field input
# error_messages -> A dictionary of __error codes to __error messages.
# initial -> day = serializers.DateField(initial=datetime.date.today)
# ------------------------
# depth = 1
"""
https://www.django-rest-framework.org/api-guide/fields/
!!! SerializerMethodField
"""


class TranslatesSerializer(serializers.ModelSerializer):
    """ TRANSLATES: To display translates related to Mark (and to add new?) """

    class Meta:
        model = Translates
        fields = ["text", "translator", "language"]


class FileMarksSerializer(serializers.ModelSerializer):
    """ TRANSLATES: FileMarks manager """
    translates_set = TranslatesSerializer(many=True, read_only=True)

    class Meta:
        model = FileMarks
        fields = ['id', 'md5sum', 'words', 'translates_set']
        extra_kwargs = {
            'md5sum': {'read_only': True},
            'words': {'read_only': True},
        }


class TransferFileSerializer(serializers.ModelSerializer):
    """ UPLOAD: On upload file serializer """
    class Meta:
        model = Files
        fields = ['owner', 'name', 'folder', 'lang_orig', 'data']


class TranslatedSerializer(serializers.ModelSerializer):
    """ To display file translate progress to other langs """
    class Meta:
        model = Translated
        # fields = '__all__'
        exclude = ['translate_copy']


class FilesSerializer(serializers.ModelSerializer):
    """ File manager serializer """
    translated_set = TranslatedSerializer(many=True, read_only=True)

    class Meta:
        model = Files
        fields = ['id', 'name', 'state', 'method', 'items', 'words', 'repo_status', 'created', 'updated', 'translated_set']
        # exclude = ['data', 'owner', 'folder', 'codec', 'options', 'repo_hash']
        extra_kwargs = {
            'state': {'read_only': True, 'source': 'get_state_display'},
            'method': {'read_only': True},
            'items': {'read_only': True},
            'words': {'read_only': True},
            'repo_status': {'read_only': True},
            # 'created': {'read_only': True},
            # 'updated': {'read_only': True},
        }


class LanguagesSerializer(serializers.ModelSerializer):
    """ To display all Languages on login """
    class Meta:
        model = Languages
        fields = ['id', 'name', 'short_name']


class FoldersSerializer(serializers.ModelSerializer):
    """ To manage and display with projects """
    class Meta:
        model = Folders
        fields = ['id', 'position', 'name', 'repo_url', 'repo_status']
        extra_kwargs = {'position': {'required': False}}


class ProjectSerializer(serializers.ModelSerializer):
    """ Project manager serializer """
    folders_set = FoldersSerializer(many=True, read_only=True)

    class Meta:
        model = Projects
        fields = ['save_id', 'icon_chars', 'name', 'lang_orig', 'translate_to', 'folders_set']
        extra_kwargs = {
            'translate_to': {'required': False, 'allow_empty': True},
            'save_id': {'read_only': True},
        }
