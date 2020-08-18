



class ProjectsApiTestCase(APITestCase):
    def test_get_list(self):
        user = Users.objects.create_user(username='a', email='a@a.ru', password='123')
        language1 = Languages.objects.create(name='Russian', short_name='ru', active=True)
        language2 = Languages.objects.create(name='English', short_name='en', active=True)
        prj1 = Projects.objects.create(name='Project1', icon_chars='P1', owner=user, lang_orig=language1)
        prj1.translate_to.set([language2])
        prj2 = Projects.objects.create(name='Project2', icon_chars='P2', owner=user, lang_orig=language1)
        prj2.translate_to.set([language2])

        url = reverse('projects-list')
        response = self.client.get(url)
        
        serializer_data = ProjectSerializer([prj1, prj2], many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
