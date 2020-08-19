import re
import random
from django.core.management.base import BaseCommand

from core.models import Files, FileMarks, Translates, Translated
from django.conf import settings
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Manager to create test data'

    def add_arguments(self, parser):
        parser.add_argument('amount', type=int, default=None)

    def handle(self, *args, **options):
        if options['amount'] is None:
            self.stderr.write('Amount not set - create one')
            return False
        self.stdout.write('Crateing basic user')
        self.create_basic()
        return False

    def create_basic(self):
        """ Create test data -> Can be used in tests """
        name = self.__random_name()
        user = User.objects.create_user(username=name, email=f'{name}@gmail.com', password='P!pp11qq')
        project = Projects.objects.create(owner=user, name=f'Project {name}', icon_chars='Pr', lang_orig=17, translate_to=[32,48])
        folder = Folders.objects.create()

    def _try_create(self, model_name, fields):
        """ To catch errors """
        try:
            obj = model_name.objects.create(**fields)
            return obj
        except Exception as e:
            print(e)
            return False
    
    def __random_name(length=0):
        name = ''
        length = length if isinstance(length, int) and length > 0 then 15
        letters_arr = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        for i in range(length):
            letter_n = random.randrange(25)
            name += letters_arr[letter_n]
        return name
