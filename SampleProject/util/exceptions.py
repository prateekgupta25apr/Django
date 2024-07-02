import traceback
from django.http import HttpResponse
import json

from main.LogManager import logger


class SampleProjectException(BaseException):
    UNKNOWN_ERROR = 500
    MISSING_REQUIRED_PARAMETERS = 400
    PAGE_NOT_FOUND = 404

    def __init__(self, error_id=500):
        self.error_id = error_id
        if error_id == 400:
            self.message = "Required parameters are not passed"
        if error_id == 404:
            self.message = "Page not found"
        else:
            self.message = "An unknown error has occurred"
        super().__init__(self.message)

    def get_error_response(self, mail_error=False, request=None):
        """Method to return response for errors"""
        # Logging error
        log_error(mail_error)

        if request is not None:
            logger.error("Error while responding the api : "+request.path)

        response = dict()
        if self.error_id == 400:
            response["message"] = self.message
            return HttpResponse(json.dumps(response),
                                content_type="application/json", status=400)
        if self.error_id == 404:
            response["message"] = self.message
            return HttpResponse(json.dumps(response),
                                content_type="application/json", status=404)
        else:
            response["message"] = self.message
            return HttpResponse(json.dumps(response),
                                content_type="application/json", status=500)


def log_error(mail_error=False):
    # Logging the exception
    logger.error(traceback.format_exc())

    # Sending email to the Manager
    if mail_error:
        email_subject = 'Error!!'
        email_message = ('Please have a look at the following error<br><br> '
                         '<div style="color:red;">' +
                         str(traceback.format_exc()).replace("\n", " <br> ") +
                         '</div>')
        #from util import send_email
        #send_email(email_subject, html_body=email_message)
