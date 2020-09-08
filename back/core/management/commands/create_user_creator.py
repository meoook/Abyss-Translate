import random
from django.core.management.base import BaseCommand

from django.contrib.auth.models import User, Permission

from core.models import Projects, Folders

# TODO: Create user by username and email - send email with password to this user


class Command(BaseCommand):
    help = 'Manager to create user with perms - creator'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, nargs='?', default=None)
        parser.add_argument('amount', type=int, nargs='*', default=None)

    def handle(self, *args, **options):
        if options['amount'] is None:
            self.stderr.write('Amount not set - create one')
        if not options['name']:
            name = self.__random_name(6)
            self.stderr.write(f'Name not set. Use random: {name}')
        else:
            name = options['name']
            self.stdout.write(f'Creating basic user name: {name}')
        self.user_reg_creator(name)
        self.stdout.write(f'Success created tested data')

    def user_reg_creator(self, name):
        """ Create test data -> Can be used in tests """
        password = '2'
        user = User.objects.create_user(username=name, email=f'{name}@gmail.com', password=password)
        self.stdout.write(f'User {name} with creator permissions registered with password: {password}')
        creator = Permission.objects.get(codename='creator')
        user.user_permissions.add(creator)

        project_props = {
            'owner': user,
            'name': f'Desert',
            'icon_chars': 'Pr',
            'lang_orig_id': 75,
        }
        project = Projects.objects.create(**project_props)
        project.translate_to.set([15, 18, 22])
        Folders.objects.create(project=project, name='Folder1', position=1)
        Folders.objects.create(project=project, name='Folder2', position=2)
    
    @staticmethod
    def __random_name(length=0):
        name = ''
        length = length if isinstance(length, int) and length > 0 else 15
        letters_arr = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                       'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        for _ in range(length):
            letter_n = random.randrange(len(letters_arr))
            name += letters_arr[letter_n]
        return name
