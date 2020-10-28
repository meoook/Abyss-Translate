from rest_framework import serializers
from rest_framework.exceptions import APIException
from django.contrib.auth.models import User

from .models import Language, Project, ProjectPermission, Folder, FolderRepo, File, ErrorFiles, Translated, \
    FileMark, Translate, TranslateChangeLog


# Extra kwargs write_only, read_only, required, default, allow_null, label
# source -> The name of the attribute that will be used to populate the field : URLField(source='get_absolute_url')
# validators - > A list of validator functions which should be applied to the incoming field input
# error_messages -> A dictionary of error codes to error messages.
# initial -> day = serializers.DateField(initial=datetime.date.today)
# ------------------------
# depth = 1


class LanguagesSerializer(serializers.ModelSerializer):
    """ To display all Language on login """
    class Meta:
        model = Language
        fields = ['id', 'name', 'short_name']


class TranslatesLogSerializer(serializers.ModelSerializer):
    """ TRANSLATES: Change log of translates """
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = TranslateChangeLog
        fields = ['translate', 'text', 'user', 'created']


class TranslatesSerializer(serializers.ModelSerializer):
    """ TRANSLATES: To display translates related to Mark (and to add new?) """
    class Meta:
        model = Translate
        fields = ["id", "text", "translator", "language"]


class FileMarksSerializer(serializers.ModelSerializer):
    """ TRANSLATES: FileMark manager. To select languages for translate. """
    translates_set = TranslatesSerializer(many=True, read_only=True)

    class Meta:
        model = FileMark
        fields = ['id', 'md5sum', 'words', 'translates_set']
        extra_kwargs = {
            'md5sum': {'read_only': True},
            'words': {'read_only': True},
        }


class TransferFileSerializer(serializers.ModelSerializer):
    """ UPLOAD: On upload file serializer """

    class Meta:
        model = File
        fields = ['id', 'name', 'folder', 'lang_orig', 'data']
        extra_kwargs = {
            'folder': {'write_only': True},
            'data': {'write_only': True},
        }


class TranslatedSerializer(serializers.ModelSerializer):
    """ To display file translate progress to other langs """
    class Meta:
        model = Translated
        exclude = ['translate_copy']


class FilesSerializer(serializers.ModelSerializer):
    """ File manager serializer """
    translated_set = TranslatedSerializer(many=True, read_only=True)

    class Meta:
        model = File
        exclude = ['data', 'folder', 'codec', 'options']
        extra_kwargs = {
            'state': {'read_only': True, 'source': 'get_state_display'},
            'method': {'read_only': True},
            'items': {'read_only': True},
            'words': {'read_only': True},
            'repo_status': {'read_only': True},
            'warning': {'read_only': True},
            'repo_sha': {'read_only': True},
            'error': {'read_only': True},
            # 'created': {'read_only': True},
            # 'updated': {'read_only': True},
        }


class FoldersSerializer(serializers.ModelSerializer):
    """ To manage and display with projects """
    files_amount = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = ['id', 'position', 'name', 'repo_url', 'repo_status', 'files_amount']
        extra_kwargs = {
            'position': {'read_only': True},
            'repo_status': {'read_only': True},
        }

    def get_files_amount(self, instance):
        return instance.files_set.count()


class FolderRepoSerializer(serializers.ModelSerializer):
    """ To manage repository options and access """
    # permission_set = serializers.ListField(child=serializers.CharField(), source='get_permission', read_only=True)

    class Meta:
        model = FolderRepo
        # fields = '__all__'
        exclude = ['access']


class PermissionsSerializer(serializers.ModelSerializer):
    """ Manage users permissions to project """

    class Meta:
        model = ProjectPermission
        fields = ["id", "permission"]


class PermsListSerializer(serializers.ModelSerializer):
    """ List of users and there rights to selected project """
    prj_perms = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'prj_perms']
        # fields = '__all__'

    def get_prj_perms(self, instance):
        save_id = self.context.get('save_id')
        qs = instance.projectpermissions_set.filter(project__save_id=save_id)
        serializer = PermissionsSerializer(qs, many=True)
        return serializer.data


class ProjectSerializer(serializers.ModelSerializer):
    """ Project manager serializer """
    permissions_set = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = Project
        exclude = ['id', 'owner']
        extra_kwargs = {
            'translate_to': {'required': False},
            'lang_orig': {'required': False},
            'save_id': {'read_only': True},
        }

    def get_permissions_set(self, instance):
        request = self.context.get('request')
        return instance.projectpermissions_set.filter(user=request.user).values_list("permission", flat=True)

    def get_author(self, instance):
        return instance.owner.username
