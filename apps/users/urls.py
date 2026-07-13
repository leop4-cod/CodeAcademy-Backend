from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import TokenPersonalizadoSerializer
from .views import (
    RegisterView,
    UserViewSet,
    UserProfileView,
    AvatarUploadView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    NotificationViewSet,
    SendNotificationView,
)


class LoginView(TokenObtainPairView):
    serializer_class = TokenPersonalizadoSerializer


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', UserProfileView.as_view(), name='user-profile'),
    path('auth/profile/avatar/', AvatarUploadView.as_view(), name='user-avatar'),
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('emails/send/', SendNotificationView.as_view(), name='send-notification'),
    path('', include(router.urls)),
]
