import random
from django.core.management.base import BaseCommand

from core.models import Projects, Folders, ProjectPermissions
from django.contrib.auth.models import User, Permission


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
        project1 = Projects.objects.create(**project1_props)
        project1.translate_to.set([15, 18, 22])
        Folders.objects.create(project=project1, name=self.__random_name(), position=1)
        Folders.objects.create(project=project1, name=self.__random_name(), position=2)
        self.stdout.write(f'Created project {project1.name} and two folders with owner:{name}')

        perms_to_create = [0, 5, 8, 9]
        for perm in perms_to_create:
            name = 'q' + str(perm)
            user = User.objects.create_user(username=name, email=f'{name}@gmail.com', password=password)
            ProjectPermissions.objects.create(user=user, project=project1, permission=perm)
            self.stdout.write(f'Created user name: {name} password:{password} with access {perm} to project {project1.name}')

        project2_props = {'owner': user, 'name': 'desert', 'icon_chars': 'P2', 'lang_orig_id': 75}
        project2 = Projects.objects.create(**project2_props)
        project2.translate_to.set([18, 22])
        self.stdout.write(f'Created second project {project2.name} with owner:{name}')

        name = 'q1'
        user = User.objects.create_user(username=name, email=f'{name}@gmail.com', password=password)
        ProjectPermissions.objects.create(user=user, project=project1, permission=0)
        ProjectPermissions.objects.create(user=user, project=project1, permission=5)
        ProjectPermissions.objects.create(user=user, project=project1, permission=8)
        ProjectPermissions.objects.create(user=user, project=project1, permission=9)
        self.stdout.write(f'Created user name: {name} password: {password} with full access to P1')

        name = 'q2'
        user = User.objects.create_user(username=name, email=f'{name}@gmail.com', password=password)
        ProjectPermissions.objects.create(user=user, project=project1, permission=0)
        ProjectPermissions.objects.create(user=user, project=project2, permission=5)
        self.stdout.write(f'Created user name: {name} password: {password} with mixed access to P1 and P2')

        self.stdout.write(' TEST DATA CREATED '.center(60, '='))
        self.stdout.write(' TOTAL USERS '.center(60, '='))
        for usr in User.objects.all():
            self.stdout.write(f'Username: {usr.username} password: {password}')
        self.stdout.write(' TOTAL PROJECTS '.center(60, '='))
        for prj in Projects.objects.all():
            self.stdout.write(f'Project name:{prj.name} id:{prj.id}')
        self.stdout.write(' TOTAL PERMISSIONS '.center(60, '='))
        for perm in ProjectPermissions.objects.all():
            self.stdout.write(f'Permission: {perm.permission} for user: {perm.user.username} to project: {perm.project.name}')
        self.stdout.write(f'{"":=<80}')    # :{filler}<{width}

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