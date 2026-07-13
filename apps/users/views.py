from rest_framework import viewsets, permissions, generics, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from .models import User, Notification
from .serializers import (
    UserSerializer, 
    UserProfileSerializer, 
    PasswordResetRequestSerializer, 
    PasswordResetConfirmSerializer,
    NotificationSerializer
)
from .permissions import EsAdministrador, EsUsuarioAutenticado


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        # Enviar correo de bienvenida (no bloquear si falla)
        try:
            send_mail(
                subject='Bienvenido a CodeAcademy',
                message=f'Hola {user.first_name or user.email},\n\nGracias por registrarte en CodeAcademy. ¡Esperamos que disfrutes de nuestros cursos!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass  # No bloquear el registro si el correo falla


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (EsUsuarioAutenticado,)

    def get_object(self):
        return self.request.user


class PasswordResetRequestView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            
            # En producción esto sería un link al frontend
            reset_link = f"http://codeacademy-api.uaeftt-ute.site/reset-password?uid={uidb64}&token={token}"
            
            try:
                send_mail(
                    subject='Recuperación de Contraseña - CodeAcademy',
                    message=f'Hola,\n\nHas solicitado restablecer tu contraseña. Usa el siguiente enlace o token para cambiarla:\n\nUID: {uidb64}\nToken: {token}\n\nEnlace (ejemplo para el frontend): {reset_link}\n\nSi no fuiste tú, ignora este mensaje.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception:
                pass  # No bloquear la respuesta si el correo falla
            return Response({'detail': 'Correo de recuperación enviado.', 'uidb64': uidb64, 'token': token}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            uid = urlsafe_base64_decode(serializer.validated_data['uidb64']).decode()
            user = User.objects.get(pk=uid)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'detail': 'Contraseña actualizada exitosamente.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = (EsUsuarioAutenticado,)

    def get_queryset(self):
        # Admins ven todas, usuarios normales solo las suyas
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Notification.objects.all()
        return Notification.objects.filter(recipient=self.request.user)

    def perform_create(self, serializer):
        # Si no se especifica recipient, se asigna al usuario autenticado
        if 'recipient' not in self.request.data:
            serializer.save(recipient=self.request.user)
        else:
            serializer.save()



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (EsAdministrador,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['email', 'first_name']
