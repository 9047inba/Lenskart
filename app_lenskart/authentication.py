from functools import wraps

from django.conf import settings
from rest_framework.response import Response
from rest_framework import status


def require_api_key(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        api_key = request.headers.get(
            "X-API-Key"
        )

        if not api_key:

            return Response({
                "message": "API key is required"
            }, status=status.HTTP_401_UNAUTHORIZED)

        if api_key != settings.API_KEY:

            return Response({
                "message": "Invalid API key"
            }, status=status.HTTP_401_UNAUTHORIZED)

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper