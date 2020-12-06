from django.urls import path
from .views import LoginAPI, AuthAPI, UserAPI, UserListAPI
from knox import views as knox_views

""" 
    !!! Attention
    As it is abyss proxy service - so no need to extend user model.
    Instead used work around. In model:
        username = abyss_user_id
        password = abyss_user_name (auth by JWT only)
        first_name = abyss_user_name#abyss_user_tag
"""

urlpatterns = [
    # path('', include('knox.urls')),
    # path('register', RegisterAPI.as_view(), name='register'),
    path('login', LoginAPI.as_view(), name='login'),
    path('auth', AuthAPI.as_view(), name='auth'),
    path('logout', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('user', UserAPI.as_view(), name='user'),
    path('users', UserListAPI.as_view(), name='users'),
]
