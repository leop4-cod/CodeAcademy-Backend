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
    AvatarUploadSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    NotificationSerializer,
    SendNotificationSerializer,
)
from .permissions import EsAdministrador, EsUsuarioAutenticado
from .email_templates import get_codeacademy_html_email


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        # Enviar correo de bienvenida (no bloquear si falla)
        try:
            nombre = user.first_name or user.email
            html_msg = get_codeacademy_html_email(
                title='¡Bienvenido a la academia!',
                content_html=f'<p>Hola <strong>{nombre}</strong>,</p><p>Gracias por registrarte en CodeAcademy. ¡Esperamos que disfrutes de nuestros cursos y potencies tu carrera al máximo nivel!</p>',
                call_to_action={'url': 'https://codeacademy-api.uaeftt-ute.site/', 'text': 'Ir a la plataforma'}
            )
            send_mail(
                subject='Bienvenido a CodeAcademy',
                message=f'Hola {nombre},\n\nGracias por registrarte en CodeAcademy. ¡Esperamos que disfrutes de nuestros cursos!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
                html_message=html_msg,
            )
        except Exception:
            pass  # No bloquear el registro si el correo falla


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (EsUsuarioAutenticado,)

    def get_object(self):
        return self.request.user


class AvatarUploadView(APIView):
    """
    PUT /api/auth/profile/avatar/
    Sube o reemplaza la foto de perfil del usuario autenticado.
    Acepta multipart/form-data con el campo 'avatar'.
    Formatos soportados: JPG, PNG, GIF, WEBP, BMP, TIFF, SVG.
    Tamaño máximo: 5MB.
    """
    permission_classes = (EsUsuarioAutenticado,)

    def put(self, request):
        user = request.user
        serializer = AvatarUploadSerializer(
            user,
            data=request.data,
            partial=False,
            context={'request': request}
        )
        if serializer.is_valid():
            # Borrar avatar anterior si existe para no acumular archivos
            if user.avatar:
                import os
                old_path = user.avatar.path
                if os.path.isfile(old_path):
                    os.remove(old_path)
            serializer.save()
            return Response(
                {
                    'detail': 'Foto de perfil actualizada correctamente.',
                    'avatar_url': serializer.data.get('avatar_url')
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Elimina la foto de perfil del usuario autenticado."""
        user = request.user
        if user.avatar:
            import os
            old_path = user.avatar.path
            if os.path.isfile(old_path):
                os.remove(old_path)
            user.avatar = None
            user.save(update_fields=['avatar'])
            return Response({'detail': 'Foto de perfil eliminada.'}, status=status.HTTP_200_OK)
        return Response({'detail': 'No tienes foto de perfil.'}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            # Buscar usuario; si no existe, responder 200 igual (no revelar qué emails existen)
            try:
                user = User.objects.get(email=email)
                token_generator = PasswordResetTokenGenerator()
                token = token_generator.make_token(user)
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

                reset_link = (
                    f"https://codeacademy-api.uaeftt-ute.site/reset-password"
                    f"?uid={uidb64}&token={token}"
                )

                html_msg = get_codeacademy_html_email(
                    title='Recuperación de Contraseña',
                    content_html=f'<p>Hola,</p><p>Has solicitado restablecer tu contraseña. Haz clic en el botón de abajo para asignar una nueva.</p><p style="margin-top:20px; font-size:14px; color:#94a3b8;">Si no fuiste tú, puedes ignorar este mensaje de forma segura.</p>',
                    call_to_action={'url': reset_link, 'text': 'Restablecer Contraseña'}
                )

                send_mail(
                    subject='Recuperación de Contraseña - CodeAcademy',
                    message=(
                        f'Hola,\n\n'
                        f'Has solicitado restablecer tu contraseña.\n\n'
                        f'UID: {uidb64}\n'
                        f'Token: {token}\n\n'
                        f'Enlace: {reset_link}\n\n'
                        f'Si no fuiste tú, ignora este mensaje.'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                    html_message=html_msg,
                )
            except User.DoesNotExist:
                pass  # No revelar que el correo no existe

            # Siempre responder 200 para no filtrar información
            return Response(
                {'detail': 'Si el correo está registrado, recibirás un enlace en tu bandeja.'},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        # Soportar tanto 'uidb64' (nombre interno Django) como 'uid' (nombre que usa la app Android)
        data = request.data.copy()
        if 'uid' in data and 'uidb64' not in data:
            data['uidb64'] = data['uid']

        serializer = PasswordResetConfirmSerializer(data=data)
        if serializer.is_valid():
            uid = urlsafe_base64_decode(serializer.validated_data['uidb64']).decode()
            user = User.objects.get(pk=uid)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(
                {'detail': 'Contraseña actualizada exitosamente.'},
                status=status.HTTP_200_OK,
            )
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


class SendNotificationView(APIView):
    """
    POST /api/emails/send/
    Solo accesible para staff/superusuarios.
    - Con user_id: envía correo al usuario indicado.
    - Sin user_id (o null): envía a todos los usuarios activos no-staff con email.
    Responde: { "detail": "...", "sent": N, "failed": M }
    """
    permission_classes = (EsAdministrador,)

    def post(self, request):
        serializer = SendNotificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        subject = serializer.validated_data['subject']
        message = serializer.validated_data['message']
        user_id = serializer.validated_data.get('user_id')

        # Determinar destinatarios
        if user_id is not None:
            recipients = User.objects.filter(pk=user_id, is_active=True)
        else:
            # Envío masivo: todos los usuarios activos no-staff con email
            recipients = User.objects.filter(
                is_active=True,
                is_staff=False,
                is_superuser=False,
            ).exclude(email='')

        sent = 0
        failed = 0
        sender = request.user

        for user in recipients:
            if not user.email:
                failed += 1
                continue
            try:
                greeting = f'Hola {user.first_name or user.email},'
                full_message = f'{greeting}\n\n{message}\n\n— El equipo de CodeAcademy'
                
                html_msg = get_codeacademy_html_email(
                    title=subject,
                    content_html=f'<p>{greeting}</p><p>{message.replace(chr(10), "<br>")}</p><p style="margin-top: 30px;">— El equipo de CodeAcademy</p>'
                )
                
                send_mail(
                    subject=subject,
                    message=full_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                    html_message=html_msg,
                )
                sent += 1
            except Exception:
                failed += 1

        detail = f'Correo enviado a {sent} usuario(s).'
        if failed > 0:
            detail += f' {failed} fallido(s).'

        return Response(
            {'detail': detail, 'sent': sent, 'failed': failed},
            status=status.HTTP_200_OK,
        )
