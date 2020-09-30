from django.urls import path
from .views import RegisterAPI, LoginAPI, UserAPI, UserListAPI, OAuth2API
from knox import views as knox_views

urlpatterns = [
    # path('', include('knox.urls')),
    path('register', RegisterAPI.as_view(), name='register'),
    path('login', LoginAPI.as_view(), name='login'),
    path('logout', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('user', UserAPI.as_view(), name='user'),
    path('usr', UserListAPI.as_view(), name='usr'),
    path('oauth/<str:code>', OAuth2API.as_view(), name='oauth'),
]
