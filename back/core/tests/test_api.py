from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User


from core.models import Languages, Projects
from core.serializers import ProjectSerializer


class ProjectsApiTestCase(APITestCase):
    # First create user -> login -> then test
    @override_settings()
    def test_project_get_list(self):
        """ Ensure we can get list of created projects """
        user = User.objects.create_user(username='a', email='a@a.ru', password='123')
        language1 = Languages.objects.create(name='Russian', short_name='ru', active=True)
        language2 = Languages.objects.create(name='English', short_name='en', active=True)
        prj1 = Projects.objects.create(name='Project1', icon_chars='P1', owner=user, lang_orig=language1)
        prj1.translate_to.set([language2])
        prj2 = Projects.objects.create(name='Project2', icon_chars='P2', owner=user, lang_orig=language1)
        prj2.translate_to.set([language2])
        self.assertEqual(Projects.objects.count(), 2)

        url = reverse('project-list')
        self.client.force_authenticate(user=user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer_data = ProjectSerializer([prj1, prj2], many=True).data
        self.assertEqual(serializer_data, response.data)
