from rest_framework import serializers
# from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


# User serializer
class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User  # settings.AUTH_USER_MODEL
        fields = ('id', 'username', 'email', 'role')

    def get_role(self, instance):
        return 'creator' if instance.has_perm('core.creator') else 'user'


# Register serializer
class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User  # settings.AUTH_USER_MODEL
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # user = settings.AUTH_USER_MODEL.objects.create_user(
        user = User.objects.create_user(
            validated_data['username'],
            validated_data['email'],
            validated_data['password'])
        return user

    @staticmethod
    def validate_password(value):
        if value.isalnum():
            raise serializers.ValidationError('password must have atleast one special character.')
        return value


# Login serializer
class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(**attrs)
        if user and user.is_active:
            return user
        raise serializers.ValidationError('Incorrect Credentials')

    class Meta:
        model = User  # settings.AUTH_USER_MODEL
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}


# Logoff serializer
