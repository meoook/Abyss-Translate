import re
import random
from django.core.management.base import BaseCommand

from core.models import Files, FileMarks, Translates, Translated, Projects, Folders
from django.conf import settings
from django.contrib.auth.models import User, Permission


class Command(BaseCommand):
    help = 'Manager to create test data'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, nargs='?', default=None)
        parser.add_argument('amount', type=int, nargs='*', default=None)

    def handle(self, *args, **options):
        if options['amount'] is None:
            self.stderr.write('Amount not set - create one')
            # return False
        if not options['name']:
            name = self.__random_name(6)
            self.stderr.write(f'Name not set. Use random: {name}')
        else:
            name = options['name']
            self.stdout.write(f'Creating basic user name: {name}')
        self.create_basic(name)
        self.stdout.write(f'Success created tested data')
        return False

    def create_basic(self, name):
        """ Create test data -> Can be used in tests """
        password = '1'
        user = User.objects.create_user(username=name, email=f'{name}@gmail.com', password=password)
        self.stdout.write(f'User {name} created with password: {password}')
        creator = Permission.objects.get(codename='creator')
        user.user_permissions.add(creator)
        # user.user_permissions.add('localize.creator')

        project_props = {
            'owner': user,
            'name': f'Project {name}',
            'icon_chars': 'Pr',
            'lang_orig_id': 75,
        }
        project = Projects.objects.create(**project_props)
        project.translate_to.set([15, 18, 22])
        folder1 = Folders.objects.create(project=project, name='Folder1', position=1)
        folder2 = Folders.objects.create(project=project, name='Folder2', position=2)

    @staticmethod
    def _try_create(model_name, fields):
        """ To catch errors """
        try:
            obj = model_name.objects.create(**fields)
            return obj
        except Exception as e:
            self.stdout.write('ERROR: create on model', model_name, e)
            return False
    
    @staticmethod
    def __random_name(length=0):
        name = ''
        length = length if isinstance(length, int) and length > 0 else 15
        letters_arr = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                       'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        for i in range(length):
            letter_n = random.randrange(25)
            name += letters_arr[letter_n]
        return name
