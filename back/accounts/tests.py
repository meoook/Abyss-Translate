from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from django.contrib.auth.models import User


class AuthSystemTestCase(APITestCase):
    def test_create_account(self):
        """ Ensure we can create a new account object """
        url = reverse('auth-register')
        data = {'username': 'DabApps', 'password': 'QwZ!3klPz', 'email': 'aa@zaz.ru'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().name, 'DabApps')

    def test_account_login(self):
        data = {'username': 'DabApps', 'password': 'QwZ!3klPz', 'email': 'aa@zaz.ru'}
        # user = User.objects.create_user(username=user_name, email='test@mail.ru', password=user_pass)
        response = self.client.login(username=data['user_name'], password=data['password'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# from django.urls import reverse
# from django.test import override_settings
# from rest_framework import status
# from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
# from django.contrib.auth.models import User

# from rest_framework.authtoken.models import Token
# from rest_framework.test import APIClient

# # Include an appropriate `Authorization:` header on all requests.
# token = Token.objects.get(user__username='lauren')
# client = APIClient()
# client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)


# class ProjectsApiTestCase(APITestCase):
#     # First create user -> login -> then test
#     @override_settings()
#     def test_get_list(self):
#         user = User.objects.create_user(username='test', email='test@mail.ru', password='123')
#         url = reverse('login')
#         response = self.client.get(url)

#         # self.assertEqual(serializer_data, response.data)

#     def test_auth_user(self):
#         factory = APIRequestFactory()
#         # By default the available formats are 'multipart' and 'json'.
#         # For compatibility with Django's existing RequestFactory the default format is 'multipart'
#         request = factory.post('/notes/', {'title': 'new idea'}, format='json')

#         # If you need to explicitly encode the request body, you can do so by setting the content_type flag
#         request = factory.post('/notes/', json.dumps({'title': 'new idea'}), content_type='application/json')
    
#     def test_for_test(self):
#         factory = APIRequestFactory()
#         user = User.objects.get(username='olivia')
#         view = AccountDetail.as_view()

#         # Make an authenticated request to the view...
#         request = factory.get('/accounts/django-superstars/')
#         force_authenticate(request, user=user)
#         response = view(request)

#     def one_more_test(self):
#         factory = APIRequestFactory()
#         user = User.objects.get(username='olivia')
#         request = factory.get('/accounts/django-superstars/')
#         force_authenticate(request, user=user, token=user.auth_token)