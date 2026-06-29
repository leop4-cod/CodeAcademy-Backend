from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def manejador_excepciones_personalizado(exc, context):
    """Devuelve mensajes de error claros y consistentes para la API."""
    response = exception_handler(exc, context)

    if response is not None:
        mensaje = _obtener_mensaje_error(response.status_code, response.data)
        response.data = {
            'error': True,
            'codigo': response.status_code,
            'mensaje': mensaje,
            'detalle': response.data,
        }
        return response

    return Response(
        {
            'error': True,
            'codigo': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'mensaje': 'Error interno del servidor. Intente nuevamente más tarde.',
            'detalle': str(exc),
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _obtener_mensaje_error(codigo, data):
    mensajes = {
        400: 'Solicitud incorrecta. Verifique los datos enviados.',
        401: 'No autenticado. Debe iniciar sesión para acceder a este recurso.',
        403: 'Acceso denegado. No tiene permisos para realizar esta acción.',
        404: 'Recurso no encontrado.',
        405: 'Método HTTP no permitido para este endpoint.',
        500: 'Error interno del servidor.',
    }
    if codigo in mensajes:
        return mensajes[codigo]
    if isinstance(data, dict) and 'detail' in data:
        return str(data['detail'])
    return 'Ha ocurrido un error al procesar la solicitud.'
