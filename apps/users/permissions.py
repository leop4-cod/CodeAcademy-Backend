from rest_framework import permissions


class EsAdministradorOReadOnly(permissions.BasePermission):
    """Usuarios autenticados pueden consultar; solo Administradores pueden crear/editar/eliminar."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.is_staff
                or request.user.is_teacher
                or request.user.groups.filter(name='Administrador').exists()
            )
        )


class EsAdministrador(permissions.BasePermission):
    """Solo miembros del grupo Administrador o superusuarios."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.is_staff
                or request.user.is_teacher
                or request.user.groups.filter(name='Administrador').exists()
            )
        )


class EsUsuarioAutenticado(permissions.BasePermission):
    """Requiere autenticación para cualquier operación."""

    def has_permission(self, request, view):
        return request.user.is_authenticated


class EsLecturaPublicaEscrituraAuth(permissions.BasePermission):
    """Consulta pública; crear requiere autenticación; editar/eliminar solo Administrador."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            return request.user.is_authenticated
        return (
            request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.is_staff
                or request.user.is_teacher
                or request.user.groups.filter(name='Administrador').exists()
            )
        )
