from django.urls import reverse
from rest_framework.test import APITestCase

from rest_framework import status
from django.contrib.auth.models import User

# from django.contrib.auth import get_user_model


class AuthSystemTestCase(APITestCase):
    def test_account_register(self):
        """ Ensure we can register a new user """
        url = reverse('register')
        data = {'username': 'DabApps', 'password': 'QwZ!3klPz', 'email': 'aa@zaz.ru'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, data['username'])
        login_status = self.client.login(username=data['username'], password=data['password'])
        self.assertEqual(login_status, True)

    def test_account_login_session(self):
        """ Ensure we can login by created user """
        data = {'username': 'DabApps', 'password': 'QwZ!3klPz', 'email': 'aa@zaz.ru'}
        user = User.objects.create_user(**data)
        login_status = self.client.login(username=data['username'], password=data['password'])
        self.assertEqual(login_status, True)

    def test_account_auth_api(self):
        """ Ensure registred user can login """
        data = {'username': 'DabApps', 'password': 'QwZ!3klPz', 'email': 'aa@zaz.ru'}
        url = reverse('register')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token = response.data.get('token')
        self.assertEqual(isinstance(token, str), True)
        self.assertEqual(len(token), 64)

        url = reverse('project-list')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        req_prj = self.client.get(url)
        self.assertEqual(req_prj.status_code, status.HTTP_200_OK)

        self.client.logout()
        login_token_logoff = self.client.get(url)
        self.assertEqual(login_token_logoff.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_api(self):
        data = {'username': 'DabApps', 'password': 'QwZ!3klPz', 'email': 'aa@zaz.ru'}
        user = User.objects.create_user(**data)

        url = reverse('login')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token = response.data.get('token')
        url = reverse('user')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_with = {'id': user.id, 'username': data['username'], 'email': data['email']}
        self.assertEqual(response.data, check_with)


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