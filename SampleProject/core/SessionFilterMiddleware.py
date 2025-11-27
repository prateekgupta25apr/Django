from django.db import connections
from django.utils.deprecation import MiddlewareMixin

from SampleProject.settings import COOKIE_NAME, COOKIE_SECRET
from prateek_gupta import configuration_properties
from prateek_gupta.utils import process_cookie
from prateek_gupta.LogManager import logger
from prateek_gupta.exceptions import log_error


class SessionFilterMiddleware(MiddlewareMixin):
    @staticmethod
    def process_request(request):
        # noinspection PyBroadException
        try:
            request.tenant_context = TenantContext(request)
            request.user_context = UserContext(request)
            logger.info("Pre processing is done")
        except Exception:
            log_error()
            request.tenant_context = TenantContext(request)
            request.user_context = UserContext(request)

    @staticmethod
    def process_response(request, response):
        response.set_cookie(COOKIE_NAME, process_cookie(False, COOKIE_SECRET,
                                                        cookie_data={"userId": 1}))
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


class TenantContext:
    """Objects of this class will be used for holding details of the current tenant"""

    def __init__(self, request):
        # noinspection PyBroadException
        try:
            use_default_schema=False
            db_schema_prefix=configuration_properties.get("db_schema_prefix",'')
            if db_schema_prefix:
                # noinspection PyBroadException
                try:
                    tenant_id = request.META.get("HTTP_TENANT_ID", "1")
                    self.schema_name = db_schema_prefix + str(tenant_id)
                    with connections['default'].cursor() as cursor:
                        cursor.execute("use " + self.schema_name)
                except Exception:
                    logger.error("Error occurred while setting schema for the tenant "
                                 "provided hence setting default schema")
                    use_default_schema=True
            else:
                use_default_schema = True

            if use_default_schema:
                self.schema_name = configuration_properties['db_default_schema']
                with connections['default'].cursor() as cursor:
                    cursor.execute("use " + self.schema_name)
        except Exception:
            log_error()
        super().__init__()


class UserContext:
    """Objects of this class will be used for holding details of the current context"""

    def __init__(self, request):
        # noinspection PyBroadException
        try:
            self.user_id = 0
            cookie = request.COOKIES.get(COOKIE_NAME, "")
            if not any(x in request.build_absolute_uri() for x in ['no-auth']):
                cookie_data = process_cookie(True, COOKIE_SECRET, cookie=cookie)
                self.user_id = cookie_data.get("userId", 0)
        except Exception:
            log_error()
        super().__init__()
