from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Language, Project, ProjectPermission, Folder, FolderRepo, File, ErrorFiles, Translated, \
    FileMark, Translate, TranslateChangeLog, MarkItem


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
    """ TRANSLATES: To display Translates related to Item and Detail """
    translator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    # user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Translate
        # fields = ['id', 'text', 'translator', 'language', 'warning']
        fields = '__all__'
        read_only_fields = ['__all__']


class ItemsSerializer(serializers.ModelSerializer):
    """ TRANSLATES: To display Items related to Mark """
    translate_set = TranslatesSerializer(many=True, read_only=True)

    class Meta:
        model = MarkItem
        fields = ["item_number", "words", "md5sum", "translate_set"]
        extra_kwargs = {
            'md5sum': {'read_only': True},
            'words': {'read_only': True},
        }


class FileMarksSerializer(serializers.ModelSerializer):
    """ TRANSLATES: FileMark manager. To select languages for translate. """
    markitem_set = ItemsSerializer(many=True, read_only=True)

    class Meta:
        model = FileMark
        fields = ['id', 'fid', 'context', 'words', 'markitem_set']
        extra_kwargs = {
            'fid': {'read_only': True},  # FIXME: mb no need
            'context': {'read_only': True},
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
    """ To display file translate progress to other languages """
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
            # 'state': {'read_only': True, 'source': 'get_state_display'},
            'method': {'read_only': True},
            'items': {'read_only': True},
            'words': {'read_only': True},
            'repo_sha': {'read_only': True},
            'repo_status': {'read_only': True},
            'warning': {'read_only': True},
            'error': {'read_only': True},
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

    @staticmethod
    def get_files_amount(instance):
        return instance.file_set.count()


class FolderRepoSerializer(serializers.ModelSerializer):
    """ To manage repository options and access """

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
        qs = instance.projectpermission_set.filter(project__save_id=save_id)
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
        return instance.projectpermission_set.filter(user=request.user).values_list("permission", flat=True)

    @staticmethod
    def get_author(instance):
        return instance.owner.username
