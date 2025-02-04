import traceback
from django.http import HttpResponse
import json

from prateek_gupta.LogManager import logger


class ServiceException(BaseException):
    MISSING_REQUIRED_PARAMETERS = 400
    UNAUTHORIZED=401
    PAGE_NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    UNKNOWN_ERROR = 500


    def __init__(self, error_id=None,message=""):
        if error_id and message:
            self.error_id=error_id
            self.message=message
        elif error_id is not None:
            self.error_id = error_id
            if error_id == 400:
                self.message = "Required parameters are not passed"
            elif error_id == 401:
                self.message = "Unauthorized"
            elif error_id == 404:
                self.message = "Page not found"
            elif error_id == 405:
                self.message = "Method not allowed"
            elif error_id == 500:
                self.message = "An unknown error has occurred"
        elif not message:
            self.message=message
            self.error_id=ServiceException.UNKNOWN_ERROR
        else:
            if not message:
                self.error_id=ServiceException.UNKNOWN_ERROR
                self.message = "An unknown error has occurred"
            else:
                self.error_id=None
        super().__init__(self.message)

    def get_error_response(self, request=None):
        """Method to return response for errors"""
        # Logging error
        log_error()

        if request is not None:
            logger.error("Error while responding the api : "+request.path)

        response = dict()
        if self.error_id is not None:
            response["message"] = self.message
            return HttpResponse(json.dumps(response),
                                content_type="application/json", status=self.error_id)
        else:
            response["message"] = self.message
            return HttpResponse(json.dumps(response),
                                content_type="application/json", status=500)


def log_error():
    # Logging the exception
    logger.error(traceback.format_exc())
