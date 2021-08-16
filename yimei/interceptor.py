from django.core.exceptions import PermissionDenied

from .api import device_check


class Interceptor:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        if '/admin/' not in request.path:
            if device_check(request):
                response = self.get_response(request)
                return response
            else:
                raise PermissionDenied("该设备无法浏览网页，请切换设备后再次查看！")
        else:
            return self.get_response(request)
