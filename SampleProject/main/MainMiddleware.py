from django.utils.deprecation import MiddlewareMixin
import jwt
from SampleProject.settings import COOKIE_NAME


class SessionFilterMiddleware(MiddlewareMixin):
    @staticmethod
    def process_request(request):
        # noinspection PyBroadException
        try:
            request.pg = jwt.decode(request.COOKIES[COOKIE_NAME], "secret",
                                    algorithms=["HS256"])
        except Exception:
            request.pg = dict()

    @staticmethod
    def process_response(request, response):
        response.set_cookie(COOKIE_NAME, jwt.encode(request.pg, "secret", algorithm="HS256"))
        return response
