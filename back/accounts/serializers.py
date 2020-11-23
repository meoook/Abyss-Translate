from rest_framework import serializers
# from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


# User serializer
class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'first_name', 'role', 'token')

    def get_role(self, instance):
        return 'creator' if instance.has_perm('core.creator') else 'user'

    def get_token(self, instance):
        return self.context.get('token')


# Register serializer
# class RegisterSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = User  # settings.AUTH_USER_MODEL
#         fields = ('id', 'username', 'email', 'password')
#         extra_kwargs = {'password': {'write_only': True}}
#
#     def create(self, validated_data):
#         # user = settings.AUTH_USER_MODEL.objects.create_user(
#         user = User.objects.create_user(
#             validated_data['username'],
#             validated_data['email'],
#             validated_data['password'])
#         return user
#
#     @staticmethod
#     def validate_password(value):
#         if value.isalnum():
#             raise serializers.ValidationError('password must have atleast one special character.')
#         return value


# Login serializer
# class LoginSerializer(serializers.ModelSerializer):
#     username = serializers.CharField()
#     password = serializers.CharField()
#
#     def validate(self, attrs):
#         user = authenticate(**attrs)
#         if user and user.is_active:
#             return user
#         raise serializers.ValidationError('Incorrect Credentials')
#
#     class Meta:
#         model = User  # settings.AUTH_USER_MODEL
#         fields = ('id', 'username', 'email', 'password')
#         extra_kwargs = {'password': {'write_only': True}}


# Logoff serializer


# User List (not creators)
class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User  # settings.AUTH_USER_MODEL
        fields = ['first_name']

