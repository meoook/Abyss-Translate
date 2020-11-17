from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.response import Response
from knox.models import AuthToken

from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, UserListSerializer
from django.contrib.auth.models import User

# cllient id - xZIGmCwMrCEjyL9hnl1fhXGD1aCDtIzNvqmnsvcK
# client secret - TSJqn5pofwZ8jAPoXVXVAHxA20wc1wWv7hZwjaje6OIqw38dXcoq0WPGY3fjyya4SkFp3OGlto2lAL2fn8gPaAo22YVHpEKlKCN8gskd5BEdKwyUvHr7yD62jXA7w5Oh


class RegisterAPI(generics.GenericAPIView):
    """ Register API """  # TODO: Turn off - users can be registered only from abyss
    serializer_class = RegisterSerializer
    permission_classes = [
        permissions.AllowAny
    ]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        _, token = AuthToken.objects.create(user)
        return Response({
            'user': UserSerializer(user, context=self.get_serializer_context()).data,
            'token': token,
        })


class LoginAPI(generics.GenericAPIView):
    """ Basic login API to retrieve auth token """
    serializer_class = LoginSerializer
    permission_classes = [
        permissions.AllowAny
    ]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        _, token = AuthToken.objects.create(user)
        return Response({
            'user': UserSerializer(user, context=self.get_serializer_context()).data,
            'token': token,
        })


class UserAPI(generics.RetrieveAPIView):
    """ Get User API """  # FIXME: Do we need it ?
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
