from django.urls import path
from rest_framework import routers
from .views import ProjectViewSet, FolderViewSet, LanguageViewSet, FileViewSet, TransferFileView, FileMarksView, ProjectPermsViewSet

router = routers.DefaultRouter()
router.register('prj/folder', FolderViewSet, 'folder')
router.register('prj/perms', ProjectPermsViewSet, 'perms' )
router.register('prj', ProjectViewSet, 'project')
router.register('lang', LanguageViewSet, 'language')
router.register('file', FileViewSet, 'file')        # Model view
router.register('transfer', TransferFileView, 'transfer')   # Upload/Download
router.register('marks', FileMarksView, 'marks')

urlpatterns = router.urls + [
    # path('test2/<int:folder_id>', get_folder_content),  # TODO: Testing
]
