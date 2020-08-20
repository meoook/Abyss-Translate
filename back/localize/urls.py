from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls'), name='auth'),
    # path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/', include('core.urls'), name='api'),
]  # + static(settings.EXPORT_URL, document_root=settings.STORAGE_EXPORT)
