import logging

from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.response import Response
from knox.models import AuthToken

from core.services.jwt_decoder import AbyssJwtValidator
from .serializers import UserSerializer, UserListSerializer
from django.contrib.auth.models import User, Permission

logger = logging.getLogger('django')


class LoginAPI(generics.GenericAPIView):
    """ Basic login API to retrieve auth token """
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        user = authenticate(**kwargs)
        if user and user.is_active:
            logger.info(f'User: {user.first_name} login with password')
            _, token = AuthToken.objects.create(user)
            return Response(self.get_serializer(user, context={'token': token}).data, status=200)
        return Response({'err': 'Incorrect Credentials'}, status=400)


class AuthAPI(generics.GenericAPIView):
    """ JWT auth from abyss - create new account or login """
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        jwt = request.data.get('key')
        if not jwt:
            return Response({'err': 'bad request'}, status=400)

        try:
            jwt_validator = AbyssJwtValidator(jwt)
        except AssertionError:
            return Response({'err': 'bad request'}, status=400)

        if not jwt_validator.valid:
            return Response({'err': 'invalid token'}, status=403)
        _data = jwt_validator.data

        _uid = _data['uuid']
        _nick = _data['nickname']
        _name = f'{_nick}#{_data["tag"]}'
        _user = {'username': _uid, 'email': None, 'password': _nick, 'first_name': _name, 'last_name': _data['lang']}

        """
        THIS CODE DON'T WORK IN VM WHEN LOGIN SECOND TIME (IN WINDOWS - OK) 
        authed_user = authenticate(username=_uid, password=_nick)
        if authed_user is not None:
            if not authed_user.is_active:
                logger.warning(f'Blocked user: {_name} try to auth by jwt')
                return Response({'err': 'no access for user'}, status=403)
            logger.info(f'User: {_name} auth with jwt')
        else:
            logger.info(f'Creating new user: {_name} from jwt data')
            authed_user = User.objects.create_user(_user)
            # TODO: check if is abyss creator or admin - if so - give permission
            creator = Permission.objects.get(codename='creator')
            authed_user.user_permissions.add(creator)
        """
        logger.info(f'TRY TO GET USER WITH UID:{_uid} {type(_uid)}')
        try:
            _authed_user = User.objects.get(username=_data['uuid'])
        except User.DoesNotExist:
            logger.info(f'Creating new user: {_name} from jwt data')
            logger.warning(f'BECAUSE NO USER WITH UID:{_uid}')
            _authed_user = User.objects.create_user(_user)
            # TODO: check if is abyss creator or admin - if so - give permission
            _role_creator = Permission.objects.get(codename='creator')
            _authed_user.user_permissions.add(_role_creator)
        else:
            if not _authed_user.is_active:
                logger.warning(f'Blocked user: {_name} try to auth by jwt')
                return Response({'err': 'no access for user'}, status=403)
            logger.info(f'User: {_name} auth with jwt')

        _, token = AuthToken.objects.create(_authed_user)
        return Response(self.get_serializer(_authed_user, context={'token': token}).data, status=200)


class UserAPI(generics.RetrieveAPIView):
    """ Get User info """
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return self.request.user


class UserListAPI(generics.ListAPIView):
    """ List of users without role - creator """
    serializer_class = UserListSerializer
    queryset = User.objects.exclude(is_staff=True, is_superuser=True)

    def list(self, request, *args, **kwargs):
        first_name = request.query_params.get('name')
        qs = self.get_queryset().exclude(Q(user_permissions__codename='creator') | Q(id=request.user.id))
        qs = qs.filter(first_name__icontains=first_name) if first_name else qs
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=200)
