from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from .models import User, Notification

# Formatos de imagen permitidos
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp', 'image/tiff', 'image/svg+xml']
MAX_AVATAR_SIZE_MB = 5


class TokenPersonalizadoSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        token['is_teacher'] = user.is_teacher
        token['is_student'] = user.is_student
        return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'is_teacher', 'is_student', 'bio', 'avatar', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        qs = User.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Ya existe un usuario con este correo electrónico.')
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        grupo_usuario, _ = Group.objects.get_or_create(name='Usuario')
        user.groups.add(grupo_usuario)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'bio', 'avatar', 'avatar_url', 'is_teacher', 'is_student')
        read_only_fields = ('id', 'email', 'is_teacher', 'is_student')
        extra_kwargs = {'avatar': {'required': False, 'allow_null': True}}

    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None


class AvatarUploadSerializer(serializers.ModelSerializer):
    """Serializer dedicado para subir/actualizar la foto de perfil."""
    avatar = serializers.ImageField(required=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('avatar', 'avatar_url')

    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None

    def validate_avatar(self, value):
        # Validar tamaño máximo
        max_size = MAX_AVATAR_SIZE_MB * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                f'La imagen es demasiado grande. El tamaño máximo permitido es {MAX_AVATAR_SIZE_MB}MB.'
            )
        # Validar tipo de contenido
        content_type = getattr(value, 'content_type', '')
        if content_type and content_type not in ALLOWED_IMAGE_TYPES:
            raise serializers.ValidationError(
                'Formato de imagen no soportado. Use JPG, PNG, GIF, WEBP, BMP, TIFF o SVG.'
            )
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    # NOTA: NO validamos si el email existe aquí para no revelar qué cuentas están registradas.
    # La vista maneja el caso de email inexistente silenciosamente.


class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data['uidb64']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("El enlace no es válido.")

        if not PasswordResetTokenGenerator().check_token(user, data['token']):
            raise serializers.ValidationError("El token es inválido o ha expirado.")

        return data


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('created_at',)


class SendNotificationSerializer(serializers.Serializer):
    """Serializer para el endpoint POST /api/emails/send/ (solo staff)."""
    subject = serializers.CharField(max_length=255)
    message = serializers.CharField()
    user_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_user_id(self, value):
        if value is not None:
            try:
                user = User.objects.get(pk=value)
            except User.DoesNotExist:
                raise serializers.ValidationError(f"No existe un usuario con id={value}.")
            if user.is_staff or user.is_superuser:
                raise serializers.ValidationError("No se puede enviar correo a un usuario staff.")
            if not user.is_active:
                raise serializers.ValidationError("El usuario indicado no está activo.")
        return value
