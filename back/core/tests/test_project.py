from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

from core.models import Languages, Projects
from core.serializers import ProjectSerializer


class ProjectsApiTestCase(APITestCase):
    # First create user -> login -> then test

    def setUp(self):
        self.user = User.objects.create_user(username='a', email='a@a.ru', password='123')
        self.lang1 = Languages.objects.create(name='Russian', short_name='ru', active=True)
        self.lang2 = Languages.objects.create(name='English', short_name='en', active=True)
        self.prj1 = Projects.objects.create(name='Project1', icon_chars='P1', owner=self.user, lang_orig=self.lang1)
        prj1.translate_to.set([self.lang2])
        self.prj2 = Projects.objects.create(name='Project2', icon_chars='P2', owner=self.user, lang_orig=self.lang1)
        prj2.translate_to.set([self.lang2])

    def test_set_up_data(self):
        """ Check setup data """
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Projects.objects.count(), 2)
        self.assertEqual(Languages.objects.count(), 2)

    def test_project_serializer(self):
        """ Ensure project serializer work properly """
        srlz_list = ProjectSerializer([self.prj1, self.prj2], many=True).data
        # to_check_with_wrong = [     # no lang_orig or 
        #     {'id': self.prj1.id, 'name': 'Project1', 'icon_chars': 'P1', 'owner': self.user.id},
        #     {'id': self.prj2.id, 'name': 'Project2', 'icon_chars': 'P2', 'owner': self.user.id},
        # ]
        # self.assertEqual([x['name'] for x in to_check_with], [x['name'] for x in srlz_list])

        to_check_with = ['Project1', 'Project2']
        self.assertEqual(to_check_with, [x['name'] for x in srlz_list])

        mock_user = {'name': 'Project cr', 'icon_chars': 'CR', 'owner': self.user.id, 'lang_orig': self.lang1.id, 'translate_to': [self.lang2.id]}
        srlz_obj = ProjectSerializer(data=mock_user)
        
        self.assertTrue(srlz_obj.is_valid())
        srlz_obj.save()
        self.asssertEqual(srlz_obj.data, mock_user)

    def test_project_get_obj(self):
        """ Ensure we can get project by API """
        pass


    @override_settings()
    def test_project_get_list(self):
        """ Ensure we can get list of projects by API """
        url = reverse('project-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer_data = ProjectSerializer([self.prj1, self.prj2], many=True).data
        self.assertEqual(serializer_data, response.data)

    def test_project_create(self):
        """ Create project by API """
        mock_user = {'name': 'Project cr', 'icon_chars': 'CR', 'owner': self.user.id, 'lang_orig': self.lang1.id, 'translate_to': [self.lang2.id]}

        url = reverse('project-create')
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, mock_user)

        self.assertEqual(mock_user, response.data)
