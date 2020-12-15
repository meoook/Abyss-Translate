import random
from django.core.management.base import BaseCommand

from core.models import Project, Folder
from django.contrib.auth.models import User, Permission
from django.core.files.base import ContentFile

from core.api.serializers import TransferFileSerializer
from core.tasks import file_uploaded_new


class Command(BaseCommand):
    help = 'Manager to create test objects to test UI'

    def handle(self, *args, **options):
        name = 'alex'
        password = '2'
        user = User.objects.create_user(username=name, email=f'{name}@gmail.com', password=password)
        creator = Permission.objects.get(codename='creator')
        user.user_permissions.add(creator)
        self.stdout.write(f'Created user name: {name} password: {password} with rights creator')

        project1_props = {'owner': user, 'name': 'snow', 'icon_chars': 'P1', 'lang_orig_id': 75}
        project1 = Project.objects.create(**project1_props)
        project1.translate_to.set([15, 18, 22])
        folder1 = Folder.objects.create(project=project1, name=self.__random_name(), position=1)
        Folder.objects.create(project=project1, name=self.__random_name(), position=2)
        self.stdout.write(f'Created project {project1.name} and two folders with owner:{name}')

        prj_lang_orig_id = 75
        file_name = 'test-file.txt'
        serializer = TransferFileSerializer(data={
            'name': file_name,
            'folder': folder1.id,
            'lang_orig': prj_lang_orig_id,
            'data': ContentFile(b"""param1, param2, param3\nbut numbers, 897, and settings\nwill be, random_setting.on, ignored\none, more, string_val\n""", file_name),
        })
        if serializer.is_valid():
            self.stdout.write(f'FILE SAVE OK')
            file_obj = serializer.save()
            # Run celery parse delay task
            file_uploaded_new(file_obj.id, prj_lang_orig_id, file_obj.data.path)
        else:
            self.stdout.write(f'FILE SAVE FAILE {serializer.errors.__str__()}')

        # file1 = File.objects.create(
        #     folder=folder1,
        #     name='test-file.txt',
        #     codec='utf-8',
        #     method='csv',  # csv, ue, html
        #     options={'any': 'data', 'more': 'info'},
        #     data='test-file.txt',
        #     items=25,
        #     words=348957,
        #     repo_sha='',
        #     repo_status=None,
        #     lang_orig_id=75,
        #     warning='',
        #     error='',
        # )
        # file_manager = LocalizeFileInterface(file1.id)
        # file_manager.create_progress()


        """ AAAAAAAAAAAAAAAAAAA """

        # self.stdout.write(f'Test file with progress created {file_name} in folder {folder1.name}')
        #
        # perms_to_create = [0, 5, 8, 9]
        # for perm in perms_to_create:
        #     name = 'limited' + str(perm)
        #     user = User.objects.create_user(username=name, email=f'{name}@gmail.com', password=password)
        #     ProjectPermission.objects.create(user=user, project=project1, permission=perm)
        #     self.stdout.write(
        #         f'Created user name: {name} password:{password} with access {perm} to project {project1.name}')
        #
        # project2_props = {'owner': user, 'name': 'desert', 'icon_chars': 'P2', 'lang_orig_id': 75}
        # project2 = Project.objects.create(**project2_props)
        # project2.translate_to.set([18, 22])
        # self.stdout.write(f'Created second project {project2.name} with owner:{name}')
        #
        # name = 'fullstack'
        # user = User.objects.create_user(username=name, email=f'{name}@gmail.com', password=password)
        # ProjectPermission.objects.create(user=user, project=project1, permission=0)
        # ProjectPermission.objects.create(user=user, project=project1, permission=5)
        # ProjectPermission.objects.create(user=user, project=project1, permission=8)
        # ProjectPermission.objects.create(user=user, project=project1, permission=9)
        # self.stdout.write(f'Created user name: {name} password: {password} with full access to P1')
        #
        # name = 'mixed'
        # user = User.objects.create_user(username=name, email=f'{name}@gmail.com', password=password)
        # ProjectPermission.objects.create(user=user, project=project1, permission=0)
        # ProjectPermission.objects.create(user=user, project=project2, permission=5)
        # self.stdout.write(f'Created user name: {name} password: {password} with mixed access to P1 and P2')
        #
        # self.stdout.write(' TEST DATA CREATED '.center(60, '='))
        # self.stdout.write(' TOTAL USERS '.center(60, '='))
        # for usr in User.objects.all():
        #     self.stdout.write(f'Username: {usr.username} password: {password}')
        # self.stdout.write(' TOTAL PROJECTS '.center(60, '='))
        # for prj in Project.objects.all():
        #     self.stdout.write(f'Project name:{prj.name} id:{prj.id}')
        # self.stdout.write(' TOTAL PERMISSIONS '.center(60, '='))
        # for perm in ProjectPermission.objects.all():
        #     self.stdout.write(
        #         f'Permission: {perm.permission} for user: {perm.user.username} to project: {perm.project.name}')
        # self.stdout.write(f'{"":=<80}')  # :{filler}<{width}

    @staticmethod
    def __random_name(length=0):
        name = ''
        length = length if isinstance(length, int) and length > 0 else 15
        letters_arr = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                       'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        for _ in range(length):
            letter_n = random.randrange(len(letters_arr))
            name += letters_arr[letter_n]
        return name.capitalize()
