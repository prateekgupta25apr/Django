import datetime

from django.db import connections
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

from prateek_gupta import configuration_properties
from prateek_gupta.LogManager import logger
from prateek_gupta.exceptions import ServiceException
from prateek_gupta.utils import process_cookie
from utils import get_error_response


class SessionFilterMiddleware(MiddlewareMixin):
    @staticmethod
    def process_request(request):
        # noinspection PyBroadException
        try:
            request.tenant_context = TenantContext(request)

            # Excluding from cookie validation
            if (
                    any(x in request.build_absolute_uri()
                        for x in [
                            "health_check",
                            "well-known",
                            "login",
                            "sign_up"
                            "forgot_password",
                            "reset_password",
                        ])
                    or
                    request.method == 'OPTIONS'
            ):
                # Creating session with default values
                request.user_context = UserContext(True, request.COOKIES)

            # Validating cookie
            else:
                request.user_context = UserContext(False, request.COOKIES)

        except ServiceException:
            return get_error_response(
                ServiceException(exception_type=ServiceException.ExceptionType.UNAUTHORIZED))

    @staticmethod
    def process_response(request, response: HttpResponse):
        response['Access-Control-Allow-Origin'] = (
            request.META.get("HTTP_ORIGIN", None)) \
            if request.META.get("HTTP_ORIGIN", None) else '*'

        response['Access-Control-Allow-Methods'] = \
            'GET, POST, PUT, DELETE, OPTIONS'

        response['Access-Control-Allow-Headers'] = \
            'Origin, X-Requested-With, Content-Type, Accept, Authorization, domain'

        response['Access-Control-Allow-Credentials'] = 'true'
        return response


class TenantContext:
    """Objects of this class will be used for holding details of the current tenant"""

    def __init__(self, request):
        # noinspection PyBroadException
        try:
            # Setting base_url and api_url in the tenant_context
            self.base_url = configuration_properties['base_url']
            self.api_url = configuration_properties['api_url']

            use_default_schema = False
            db_schema_prefix = configuration_properties.get("db_schema_prefix", '')
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
                    use_default_schema = True
            else:
                use_default_schema = True

            if use_default_schema:
                self.schema_name = configuration_properties['db_default_schema']
                with connections['default'].cursor() as cursor:
                    cursor.execute("use " + self.schema_name)
        except Exception:
            logger.error("An error occurred while setting base_url in current session")
        super().__init__()


class UserContext:
    """Objects of this class will be used for holding details of the current context of
    the user and also manage cookie validation"""

    user_jwt_map = {}
    """This field stores the value to be stored in user_jwt_map when user is logged out"""
    logged_out_key = "LOGGED_OUT"

    def __init__(self, no_auth,cookies):
        cookie_name = configuration_properties['cookie_name']
        cookie_secret = configuration_properties['cookie_secret']

        # Extracting Cookie from the request using cookie_name
        cookie = cookies.get(cookie_name, None)

        # noinspection PyBroadException
        try:
            # Decoding cookie
            cookie_data = process_cookie(
                True, cookie_secret, cookie=cookie, algorithms=["HS256"])

            # Setting JWT
            self.jwt = cookie if cookie else ""

            # Setting dark_mode.Default is False
            self.dark_mode = cookie_data.get("dark_mode", False)

            # Setting is_mobile_api. Default is False
            self.is_mobile_api = cookie_data.get("is_mobile_api", False)

            # Setting user_id. Default is 0
            self.user_id = cookie_data.get("user_id", 0)

            # Setting user_logout_time. Default is 0
            self.user_logout_time = cookie_data.get("user_logout_time", 0)

            # Validating if user should be allowed or not
            self.validate_cookie(no_auth)

        except Exception:
            # If any error occurs while processing cookie
            self.handle_cookie_exception(no_auth=no_auth)

        super().__init__()

    def validate_cookie(self, no_auth):
        """This method validates cookie based on time and jwt, and in case cookie is not valid
        we throw error"""
        # This validates if the user is logged out based on time
        time_based_validation = (
            # Validating whether the logout time in jwt is greater than or not
            (self.user_logout_time <= datetime.datetime.now().timestamp() * 1000)
            and
            # Validating if user has asked to remember
            self.user_logout_time != -1
        )

        # This method validates and returns True only if the user is logged out
        # This validates if the user is logged out based on jwt
        jwt_based_validation = (
            # Validating if the provided jwt is in our record
            self.user_jwt_map.get(self.user_id, None)
            and
            # Once we log out the user, we store the value of self.logged_out_key
            # against the userId in the dict user_jwt_map
            self.user_jwt_map.get(self.user_id) == self.logged_out_key
            and
            # Validating is cached JWT and provided JWT are NOT same
            # (for scenarios when user re-logins with old jwt)
            self.user_jwt_map.get(self.user_id, None) != self.jwt
        )

        if time_based_validation or jwt_based_validation:
            self.handle_cookie_exception(no_auth=no_auth)

    def handle_cookie_exception(self, no_auth=False):
        """This method throw exception if cookie is not valid ONLY if cookie_validation is set
        to true and no_auth is set to false"""
        cookie_validation = configuration_properties.get('cookie_validation', None)

        if cookie_validation and str(cookie_validation).lower() == "true" and not no_auth:
            raise ServiceException(
                exception_type=ServiceException.ExceptionType.UNAUTHORIZED)
        else:
            self.jwt = ""
            self.dark_mode = False
            self.is_mobile_api = False
            self.user_id = 0
            self.user_logout_time = 0

    def update_session_for_logout(self, request):
        """This method clears the user details from the user_jwt_map"""
        self.user_jwt_map[request.user_context.user_id] = self.logged_out_key

    def update_session_for_login(
            self, user_details, response):
        """This method uses provided user details to prepare cookie and set the
        cookie in the 'response' object and user_jwt_map, ONLY IF USER IS LOGGED IN"""

        # Setting Cookie only if the user is logged in
        if "user_id" in user_details and user_details["user_id"] > 0:
            cookie_name = configuration_properties['cookie_name']
            cookie_secret = configuration_properties['cookie_secret']

            jwt_token = process_cookie(
                False, cookie_secret, cookie_data=user_details, algorithms=["HS256"])

            # Updating user_jwt_map
            self.user_jwt_map[user_details["user_id"]] = jwt_token

            # Setting cookie data in Cookie
            response.set_cookie(cookie_name, jwt_token)
