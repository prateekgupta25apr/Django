from django.utils.deprecation import MiddlewareMixin

from SampleProject.settings import COOKIE_NAME
from prateek_gupta import process_cookie
from prateek_gupta.LogManager import logger
from prateek_gupta.exceptions import log_error


class SessionFilterMiddleware(MiddlewareMixin):

    def __init__(self, get_response):
        self.cookie_name=COOKIE_NAME
        super().__init__(get_response)


    def process_request(self,request):
        # noinspection PyBroadException
        try:
            cookie=request.COOKIES.get(self.cookie_name, "")
            request.current_session = CurrentSession(request,cookie)
            logger.info("Pre processing is done")
        except Exception:
            log_error()
            request.current_session = CurrentSession(request)

    @staticmethod
    def process_response(request, response):
        response.set_cookie()
        response['Access-Control-Allow-Origin'] = (
            request.META.get("HTTP_ORIGIN", None)) \
            if request.META.get("HTTP_ORIGIN", None) else '*'

        response['Access-Control-Allow-Methods'] = \
            'GET, POST, PUT, DELETE, OPTIONS'

        response['Access-Control-Allow-Headers'] = \
            ('Origin, X-Requested-With, Content-Type, Accept, Authorization, '
             'wolken_token, domain')

        response['Access-Control-Allow-Credentials'] = 'true'
        logger.info("Post processing is done")
        return response


class CurrentSession:
    """Objects of this class will be used for details of the current session"""
    def __init__(self,request,cookie):
        # noinspection PyBroadException
        try:
            if not any(x in request.build_absolute_uri() for x in ['no-auth']):
                process_cookie(True,"",cookie=cookie)
        except Exception:
            log_error()
        super().__init__()


