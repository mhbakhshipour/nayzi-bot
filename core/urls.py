from django.urls import path
from core.views import *

urlpatterns = [
    path('api/v1/user/list', UserServiceView.as_view(), name='api_get_user_list'),
    path('api/v1/user/<int:user_id>', UserDetailView.as_view(), name='api_edit_user_detail'),
    path('api/v1/auth/login', LoginView.as_view(), name='refresh_token'),
    path('api/v1/auth/token/refresh', TokenRefreshView.as_view(), name='refresh_token'),
]
