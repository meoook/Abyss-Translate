from rest_framework import serializers
from rest_framework.exceptions import APIException

from .models import Languages, Projects, ProjectPermissions, Folders, FolderRepo, Files, ErrorFiles, Translated, FileMarks, Translates 

# Extra kwargs write_only, read_only, required, default, allow_null, label
# source -> The name of the attribute that will be used to populate the field : URLField(source='get_absolute_url')
# validators - > A list of validator functions which should be applied to the incoming field input
# error_messages -> A dictionary of error codes to error messages.
# initial -> day = serializers.DateField(initial=datetime.date.today)
# ------------------------
# depth = 1


class LanguagesSerializer(serializers.ModelSerializer):
    """ To display all Languages on login """
    class Meta:
        model = Languages
        fields = ['id', 'name', 'short_name']


class TranslatesSerializer(serializers.ModelSerializer):
    """ TRANSLATES: To display translates related to Mark (and to add new?) """
    class Meta:
        model = Translates
        fields = ["text", "translator", "language"]


class FileMarksSerializer(serializers.ModelSerializer):
    """ TRANSLATES: FileMarks manager. To select languages for translate. """
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
        model = Files
        exclude = ['data', 'folder', 'codec', 'options', 'repo_hash']
        extra_kwargs = {
            'state': {'read_only': True, 'source': 'get_state_display'},
            'method': {'read_only': True},
            'items': {'read_only': True},
            'words': {'read_only': True},
            'repo_status': {'read_only': True},
            # 'created': {'read_only': True},
            # 'updated': {'read_only': True},
        }


class FoldersSerializer(serializers.ModelSerializer):
    """ To manage and display with projects """

    class Meta:
        model = Folders
        fields = ['id', 'project', 'position', 'name', 'repo_url', 'repo_status']
        extra_kwargs = {
            'position': {'read_only': True},
            'project': {'write_only': True, 'required': False},
            # 'repo_url': {'required': False},
            'repo_status': {'read_only': True},
        }


class FolderRepoSerializer(serializers.ModelSerializer):
    """ To manage repository options and access """
    # permission_set = serializers.ListField(child=serializers.CharField(), source='get_permission', read_only=True)

    class Meta:
        model = FolderRepo
        fields = '__all__'
        extra_kwargs = {
            'access': {'write_only': True},     # 'required': False
            'folder': {'write_only': True},
        }


class PermissionsSerializer(serializers.ModelSerializer):
    """ Manage users permissions to project (project id must be hidden) """

    class Meta:
        model = ProjectPermissions
        fields = ["id", "user", "project", "permission"]
        extra_kwargs = {
            'user': {'source': 'user.username'},
            'project': {'source': 'project.save_id'},  # , 'write_only': True},
        }


class ProjectSerializer(serializers.ModelSerializer):
    """ Project manager serializer (project id must be hidden) """
    permissions_set = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = Projects
        exclude = ['id', 'owner']
        extra_kwargs = {
            'translate_to': {'required': True},
            'save_id': {'read_only': True},
        }

    def get_permissions_set(self, instance):
        request = self.context.get('request')
        return instance.projectpermissions_set.filter(user=request.user).values_list("permission", flat=True) if request else []

    def get_author(self, instance):
        return instance.owner.username
