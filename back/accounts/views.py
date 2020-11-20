import base64

from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.response import Response
from knox.models import AuthToken

from core.services.jwt_decoder import AbyssJwtValidator
from .serializers import UserSerializer, UserListSerializer
# from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, UserListSerializer
from django.contrib.auth.models import User


class LoginAPI(generics.GenericAPIView):
    """ JWT auth from abyss - create new account or login """
    serializer_class = UserSerializer
    permission_classes = [
        permissions.AllowAny
    ]

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

        data = jwt_validator.data
        uid = data['uuid']
        nick = data['nickname']

        user = authenticate(username=uid, password=nick)
        if user:
            if not user.is_active:
                return Response({'err': 'no access for user'}, status=403)
        else:
            user = User.objects.create_user(username=uid,
                                            email=None,
                                            password=nick,
                                            first_name=f'{nick}#{data["tag"]}',
                                            last_name=data['lang'])
        _, token = AuthToken.objects.create(user)
        return Response(UserSerializer(user, context={'token': token}).data)


class UserAPI(generics.RetrieveAPIView):
    """ Get User API """
    serializer_class = UserSerializer
    permission_classes = [
        permissions.AllowAny
    ]

    def get_object(self):
        return self.request.user


class UserListAPI(generics.ListAPIView):
    """ List of users without role - creator """
    serializer_class = UserListSerializer
    queryset = User.objects.exclude(is_staff=True, is_superuser=True)

    def list(self, request, *args, **kwargs):
        username = request.query_params.get('name')
        qs = self.get_queryset().exclude(Q(user_permissions__codename='creator') | Q(id=request.user.id))
        qs = qs.filter(username__icontains=username) if username else qs
        serializer = UserListSerializer(qs, many=True)
        return Response(serializer.data, status=200)
