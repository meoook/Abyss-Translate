from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.response import Response
from knox.models import AuthToken
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, UserListSerializer
from django.contrib.auth.models import User


# Register API
class RegisterAPI(generics.GenericAPIView):
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


# Login API
class LoginAPI(generics.GenericAPIView):
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


# Get User API
class UserAPI(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [
        permissions.AllowAny
    ]

    def get_object(self):
        return self.request.user


# List not creator Users
class UserListAPI(generics.ListAPIView):
    serializer_class = UserListSerializer
    queryset = User.objects.exclude(is_staff=True, is_superuser=True)

    def list(self, request, *args, **kwargs):
        username = request.query_params.get('name')
        qs = self.get_queryset().exclude(Q(user_permissions__codename='creator') | Q(id=request.user.id))
        qs = qs.filter(username__icontains=username) if username else qs
        serializer = UserListSerializer(qs, many=True)
        return Response(serializer.data, status=200)
