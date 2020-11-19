import base64

from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.response import Response
from knox.models import AuthToken

from .serializers import UserSerializer, UserListSerializer
# from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, UserListSerializer
from django.contrib.auth.models import User

# cllient id - xZIGmCwMrCEjyL9hnl1fhXGD1aCDtIzNvqmnsvcK
# client secret - TSJqn5pofwZ8jAPoXVXVAHxA20wc1wWv7hZwjaje6OIqw38dXcoq0WPGY3fjyya4SkFp3OGlto2lAL2fn8gPaAo22YVHpEKlKCN8gskd5BEdKwyUvHr7yD62jXA7w5Oh


# class RegisterAPI(generics.GenericAPIView):
#     """ Register API """  # TODO: Turn off - users can be registered only from abyss
#     serializer_class = RegisterSerializer
#     permission_classes = [
#         permissions.AllowAny
#     ]
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         _, token = AuthToken.objects.create(user)
#         return Response({
#             'user': UserSerializer(user, context=self.get_serializer_context()).data,
#             'token': token,
#         })

def jwt_decode(jwt: str):
    SECRET_KEY = 'cAtwa1kkEy'
    print('JWT IS', jwt)
    jwt_parts = jwt.split('.')
    if len(jwt_parts) != 3:
        return False
    # try:
    part0 = jwt_parts[0].encode()
    print(part0)
    header = base64.urlsafe_b64decode(jwt_parts[0].encode())
    print('HEADER IS', header)
    part1 = jwt_parts[1].encode()
    print(part1)
    payload = base64.urlsafe_b64decode(jwt_parts[1].encode())
    print('PAYLOAD IS', payload)
    part2 = jwt_parts[2].encode()
    print(part2)
    signature = base64.urlsafe_b64decode(jwt_parts[2].encode())
    print('SIGNATURE IS', signature)
    # except ValueError:
    #     print("ERRRRRRRRRRRRORRRRRRRRRRR")
    #     return False

    return True


class LoginAPI(generics.GenericAPIView):
    """ JWT auth from abyss - create new account or login """
    serializer_class = UserSerializer
    permission_classes = [
        permissions.AllowAny
    ]

    def post(self, request, *args, **kwargs):
        jwt = request.data.get('key')
        if not jwt:
            Response({'err': 'bad request'}, status=400)
        jwt_decode(jwt)
        # uid = jwt['uid']
        # username = jwt['name']
        return Response({'err': 'no access for user'}, status=403)
        #
        # if not username or not uid:
        #     return Response({'err': 'invalid key'}, status=403)
        #
        # user = authenticate({'username': uid, 'password': username})
        # if user:
        #     if user.is_active:
        #         pass
        #         # return user
        #     else:
        #         return Response({'err': 'no access for user'}, status=403)
        # else:
        #     user = User.objects.create_user(uid, email=None, password=username)
        # _, token = AuthToken.objects.create(user)
        # # return Response({
        # #     'user': UserSerializer(user, context={'token': token}).data,
        # #     'token': token,
        # # })

        # return Response(UserSerializer(user, context={'token': token}).data)


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
