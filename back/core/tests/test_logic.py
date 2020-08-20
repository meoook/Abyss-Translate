from django.test import TestCase

from django.contrib.auth.models import User

from core.models import Languages, Projects
from core.serializers import ProjectSerializer


class ProjectsSerializerTestCase(TestCase):
    def test_project_list(self):
        user = User.objects.create_user(username='a', email='a@a.ru', password='123')
        language1 = Languages.objects.create(name='Russian', short_name='ru', active=True)
        language2 = Languages.objects.create(name='English', short_name='en', active=True)
        prj1 = Projects.objects.create(name='Project1', icon_chars='P1', owner=user, lang_orig=language1)
        prj1.translate_to.set([language2])
        prj2 = Projects.objects.create(name='Project2', icon_chars='P2', owner=user, lang_orig=language1)
        prj2.translate_to.set([language2])

        data = ProjectSerializer([prj1, prj2], many=True).data
        to_check_with = [
            {'id': prj1.id, 'name': 'Project1', 'icon_chars': 'P1', 'owner': user.username},
            {'id': prj2.id, 'name': 'Project2', 'icon_chars': 'P2', 'owner': user.username},
        ]

        self.assertEqual([x['name'] for x in to_check_with], [x['name'] for x in data])
