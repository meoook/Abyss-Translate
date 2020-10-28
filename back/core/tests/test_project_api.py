from django.urls import reverse
from rest_framework import status
from rest_framework.utils import json
from rest_framework.test import APITestCase

from django.contrib.auth.models import User, Permission
from core.models import Language, Project, ProjectPermission
from core.serializers import ProjectSerializer


class ProjectsApiTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('project-list')
        creator = Permission.objects.get(codename='creator')
        self.user1 = User.objects.create_user(username='a', email='a@a.ru', password='123')
        self.user1.user_permissions.add(creator)
        self.user2 = User.objects.create_user(username='b', email='b@b.ru', password='123')
        self.lang1 = Language.objects.get(name='Russian')
        self.lang2 = Language.objects.get(name='English')
        self.prj1 = Project.objects.create(name='Project1', icon_chars='P1', owner=self.user1, lang_orig=self.lang1)
        self.prj1.translate_to.set([self.lang2])
        self.prj2 = Project.objects.create(name='Project2', icon_chars='P2', owner=self.user1, lang_orig=self.lang1)
        self.prj2.translate_to.set([self.lang2])

        self.mock_prj = {
            'name': 'Project create',
            'icon_chars': 'CR',
            'owner': self.user1.id,
            'lang_orig': self.lang1.id,
            'translate_to': [self.lang2.id],
        }

    def test_set_up_data(self):
        """ Check setup data """
        self.assertEqual('/api/prj/', self.url)
        self.assertEqual(2, User.objects.count())
        self.assertEqual(2, Project.objects.count())
        self.assertEqual(96, Language.objects.count())
        self.assertEqual(2, self.user1.projects_set.count())
        self.assertEqual(0, self.user2.projects_set.count())
        self.assertEqual(1, User.objects.with_perm('core.creator').count())

    def test_project_serializer(self):
        """ Ensure project serializer work properly """
        serializer_data = ProjectSerializer([self.prj1, self.prj2], many=True).data
        to_check_with = ['Project1', 'Project2']
        self.assertEqual(to_check_with, [x['name'] for x in serializer_data])

        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

        srlz_obj = ProjectSerializer(data=self.mock_prj)
        self.assertTrue(srlz_obj.is_valid())
        srlz_obj.save()
        self.assertEqual(self.mock_prj['name'], srlz_obj.data.get('name'))

        # GET LIST
    def test_project_owner_get_list(self):
        """ API - Get list of projects where user is owner """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))

    def test_project_access_get_list(self):
        """ API - Check get list response if changing permissions """

        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

        self.client.force_authenticate(user=self.user2)

        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, len(response.data))

        ProjectPermission.objects.create(user=self.user2, project=self.prj1, permission=0)
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data))
        self.assertEqual(str(self.prj1.save_id),  response.data[0]['save_id'])
        self.assertEqual([0],  response.data[0]['permissions_set'])

        ProjectPermission.objects.create(user=self.user2, project=self.prj1, permission=5)
        ProjectPermission.objects.create(user=self.user2, project=self.prj1, permission=8)
        ProjectPermission.objects.create(user=self.user2, project=self.prj1, permission=9)
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data))
        self.assertEqual([0, 5, 8, 9], response.data[0].get('permissions_set'))

        test_perm = ProjectPermission.objects.create(user=self.user2, project=self.prj2, permission=0)
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))
        self.assertEqual(str(self.prj2.save_id),  response.data[1]['save_id'])
        self.assertEqual([0], response.data[1].get('permissions_set'))

        test_perm.delete()
        test_perm = ProjectPermission.objects.create(user=self.user2, project=self.prj2, permission=5)
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))
        self.assertEqual(str(self.prj2.save_id),  response.data[1]['save_id'])
        self.assertEqual([5], response.data[1].get('permissions_set'))

        test_perm.delete()
        test_perm = ProjectPermission.objects.create(user=self.user2, project=self.prj2, permission=8)
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))
        self.assertEqual(str(self.prj2.save_id),  response.data[1]['save_id'])
        self.assertEqual([8], response.data[1].get('permissions_set'))

        test_perm.delete()
        ProjectPermission.objects.create(user=self.user2, project=self.prj2, permission=9)
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))
        self.assertEqual(str(self.prj2.save_id),  response.data[1]['save_id'])
        self.assertEqual([9], response.data[1].get('permissions_set'))

    # POST
    def test_project_create(self):
        """ Create project by API """
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.url, data=json.dumps({**self.mock_prj}), content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        created_prj_related_to_user = self.user1.projects_set.filter(save_id=response.data.get('save_id'))
        self.assertEqual(1, created_prj_related_to_user.count())
        self.assertEqual(self.mock_prj['name'], created_prj_related_to_user[0].name)

    def test_project_create_no_rights(self):
        """ User without 'localize.creator' permission cant's create """
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(self.url, self.mock_prj)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

