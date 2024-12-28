from django.urls import path
from .views import RegisterAPIView, LoginAPIView, FolderAPIView, FileAPIView

urlpatterns = [
    # JWT Token Endpoints
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Authentication Endpoints
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),

    # Folder Endpoints
    path('folders/', FolderAPIView.as_view(), name='folders'),  # List/Create Root Folders
    path('folders/<int:folder_id>/', FolderAPIView.as_view(), name='subfolders'),  # List/Create Subfolders

    # File Endpoints
    path('files/', FileAPIView.as_view(), name='files'),  # List/Create Files
    path('folders/<int:folder_id>/files/', FileAPIView.as_view(), name='folder_files'),  # Create File in a Folder
    path('folders/<int:folder_id>/files/<int:file_id>/', FileAPIView.as_view(), name='file_details'),  # Update/Delete specific file
    path('files/<int:file_id>/', FileAPIView.as_view(), name='file_details'),  # Update/Delete specific file (outside folder)
]
