# urbanfoods/middleware.py
from django.conf import settings
from importlib import import_module

class CustomAdminSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.user_engine = import_module(settings.SESSION_ENGINE)
        self.admin_engine = import_module(settings.ADMIN_SESSION_ENGINE)

    def __call__(self, request):
        # If it's admin-panel, use admin session
        if request.path.startswith("/admin-panel/"):
            session_key = request.COOKIES.get(settings.ADMIN_SESSION_COOKIE_NAME, None)
            request.session = self.admin_engine.SessionStore(session_key)
            request.session_cookie_name = settings.ADMIN_SESSION_COOKIE_NAME
        else:
            session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
            request.session = self.user_engine.SessionStore(session_key)
            request.session_cookie_name = settings.SESSION_COOKIE_NAME

        response = self.get_response(request)

        # Save session back under correct cookie name
        if getattr(request, "session", None) and request.session.modified:
            cookie_name = getattr(request, "session_cookie_name", settings.SESSION_COOKIE_NAME)
            response.set_cookie(
                cookie_name,
                request.session.session_key,
                httponly=True,
                secure=False,  # set True in production with HTTPS
                samesite="Lax"
            )

        return response
