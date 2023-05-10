from django.conf import settings
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from users.models import ApiKey


class APIKeyMiddleware(MiddlewareMixin):
    def process_request(self, request):
        http_api_key = request.META.get('HTTP_API_KEY', None)
        check = request.path.startswith(tuple(settings.EXCLUDED_PATHS))
        check_api = request.path.startswith(tuple(settings.API_PATHS))
        if check or request.method == "OPTIONS":
            return None
        if check_api:
            try:
                if ApiKey.objects.filter(api_key=http_api_key).exists():
                    return None
            except Exception as e:
                pass
            return HttpResponseForbidden('Oops... Note: You do not have have access to apis.')
        return None


class AdminStaticMiddleware(MiddlewareMixin):
    def process_request(self, request):
        check = request.path.startswith(tuple(["/static/admin"]))
        session_id = request.COOKIES.get("sessionid")
        if check and session_id:
            return None
        elif check and not session_id:
            return HttpResponseForbidden('Unauthorized')
        else:
            return None
