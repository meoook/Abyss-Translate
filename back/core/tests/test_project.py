from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User, Permission
from rest_framework.utils import json

from core.models import Languages, Projects, ProjectPermissions
from core.serializers import ProjectSerializer


class ProjectsApiTestCase(APITestCase):
    # First create user -> login -> then test

    def setUp(self):
        self.url = reverse('project-list')
        creator = Permission.objects.get(codename='creator')
        # translator = Permission.objects.get(codename='translator')
        # admin = Permission.objects.get(codename='admin')
        self.user1 = User.objects.create_user(username='a', email='a@a.ru', password='123')
        self.user1.user_permissions.add(creator)
        self.user2 = User.objects.create_user(username='b', email='b@b.ru', password='123')
        # self.user3 = User.objects.create_user(username='c', email='c@c.ru', password='123')
        # self.user2.user_permissions.add(translator)
        self.lang1 = Languages.objects.create(name='Russian', short_name='ru', active=True)
        self.lang2 = Languages.objects.create(name='English', short_name='en', active=True)
        self.prj1 = Projects.objects.create(name='Project1', icon_chars='P1', owner=self.user1, lang_orig=self.lang1)
        self.prj1.translate_to.set([self.lang2])
        self.prj2 = Projects.objects.create(name='Project2', icon_chars='P2', owner=self.user1, lang_orig=self.lang1)
        self.prj2.translate_to.set([self.lang2])

        self.mock_prj = {
            'name': 'Project create',
            'icon_chars': 'CR',
            'owner_id': self.user1.id,
            'lang_orig': self.lang1.id,
            'translate_to': [self.lang2.id],
        }

    def test_set_up_data(self):
        """ Check setup data """
        self.assertEqual('/api/prj/', self.url)
        self.assertEqual(3, User.objects.count())
        self.assertEqual(2, Projects.objects.count())
        self.assertEqual(2, Languages.objects.count())
        self.assertEqual(2, self.user1.projects_set.count())
        self.assertEqual(0, self.user2.projects_set.count())
        self.assertEqual(1, User.objects.with_perm('core.creator'))
        # self.assertEqual(1, User.objects.with_perm('core.translator'))

    def test_project_serializer(self):
        """ Ensure project serializer work properly """
        serializer_data = ProjectSerializer([self.prj1, self.prj2], many=True).data
        srlz_list = ProjectSerializer([self.prj1, self.prj2], many=True).data
        to_check_with = ['Project1', 'Project2']
        self.assertEqual(to_check_with, [x['name'] for x in serializer_data])

        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

        srlz_obj = ProjectSerializer(data=self.mock_prj)
        self.assertTrue(srlz_obj.is_valid())
        srlz_obj.save()
        self.assertEqual(srlz_obj.data, self.mock_prj)


    def test_project_get_obj(self):
        """ Ensure we can get project by API """
        pass

    @override_settings()
    def test_project_owner_get_list(self):
        """ API - Get list of projects where user is owner """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        assert 2 == len(response.data)

    def test_project_translator_get_list(self):
        """ API - Get list of projects where user is translator """
        self.client.force_authenticate(user=self.user2)
        ProjectPermissions.objects.create(user=self.user2, project=self.prj1, permission=0)
        response = self.client.get(self.url)
        assert status.HTTP_200_OK == response.status_code
        assert 1 == len(response.data)
        ProjectPermissions.objects.create(user=self.user2, project=self.prj2, permission=0)
        response = self.client.get(self.url)
        assert status.HTTP_200_OK == response.status_code
        assert 2 == len(response.data)

    def test_project_invite_get_list(self):
        """ API - Get list of projects where user is translator """
        """ Ensure we can get list of projects by API """
        ProjectPermissions.objects.create(user=self.user2, project=self.prj1, permission=5)
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.url)
        assert status.HTTP_200_OK == response.status_code
        assert 1 == len(response.data)

    def test_project_manage_get_list(self):
        """ API - Get list of projects where user is translator """
        """ Ensure we can get list of projects by API """
        ProjectPermissions.objects.create(user=self.user2, project=self.prj1, permission=8)
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.url)
        assert status.HTTP_200_OK == response.status_code
        assert 1 == len(response.data)

    def test_project_admin_get_list(self):
        """ API - Get list of projects where user is translator """
        ProjectPermissions.objects.create(user=self.user2, project=self.prj1, permission=9)
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.url)
        assert status.HTTP_200_OK == response.status_code
        assert 1 == len(response.data)

    def test_project_no_access_get_list(self):
        """ API - Get list of projects where user is translator """
        """ Check other users have no access users projects """
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_project_access_get_list(self):
        """ API - Check project permissions in response """
        ProjectPermissions.objects.create(user=self.user2, project=self.prj1, permission=0)
        ProjectPermissions.objects.create(user=self.user2, project=self.prj1, permission=5)
        ProjectPermissions.objects.create(user=self.user2, project=self.prj1, permission=8)
        ProjectPermissions.objects.create(user=self.user2, project=self.prj1, permission=9)
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        assert 1 == len(response.data)
        assert [0, 5, 8, 9] == response.data.get('permissions_set')


    def test_project_create(self):
        """ Create project by API """
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(url, json.dumps(self.mock_prj), content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        created_prj_related_to_user = self.user1.projects_set.filter(save_id=response.data.get('save_id'))
        self.assertEqual(1, created_prj_related_to_user.count())
        self.assertEqual(self.mock_prj['name'], created_prj_related_to_user[0].name)

    def test_project_create_no_rights(self):
        """ User without 'localize.creator' permission cant's create """
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(self.url, self.mock_prj)
        self.assertEqual(0, len(response.data))
        self.assertEqual(self.mock_prj, response.data.get('name'))  # False


