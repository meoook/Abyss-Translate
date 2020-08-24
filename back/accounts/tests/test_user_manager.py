from django.contrib.auth import get_user_model
# from django.contrib.auth.models import User
from django.db.utils import IntegrityError

from django.test import TestCase


class UsersManagersTests(TestCase):

    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(username='normal', email='normal@user.com', password='foo')
        user2 = User.objects.create_user(username='normal2', password="foo")
        self.assertEqual(2, User.objects.count())

        self.assertEqual('normal', user.username)
        self.assertEqual('normal@user.com', user.email)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        # try:
        #     # username is None for the AbstractUser option
        #     # username does not exist for the AbstractBaseUser option
        #     self.assertIsNone(user.username)
        # except AttributeError:
        #     pass
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):
            User.objects.create_user(email='')
        with self.assertRaises(ValueError):
            User.objects.create_user(username='', password="foo")
        with self.assertRaises(ValueError):
            User.objects.create_user(username='', email='x@x.ru', password="foo")
        with self.assertRaises(IntegrityError):
            User.objects.create_user(username='normal', password="foo")   # Same username
        # self.assertRaises(ValueError, User.objects.create_user(username='', email='', password="secret"))
        # self.assertRaises(ValueError, User.objects.create_user(username='xxx', email='', password=''))
        # self.assertRaises(ValueError, User.objects.create_user(username='xxx', email='x@x.ru', password=''))

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser('super', 'super@user.com', 'foo')
        self.assertEqual('super', admin_user.username)
        self.assertEqual('super@user.com', admin_user.email)
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        # try:
        #     # username is None for the AbstractUser option
        #     # username does not exist for the AbstractBaseUser option
        #     self.assertIsNone(admin_user.username)
        # except AttributeError:
        #     pass
        with self.assertRaises(ValueError):
            User.objects.create_superuser(username='super', email='super@user.com', password='foo', is_superuser=False)
