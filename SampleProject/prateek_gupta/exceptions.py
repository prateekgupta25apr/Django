import traceback
from enum import Enum

import prateek_gupta
from prateek_gupta.LogManager import logger


class ServiceException(Exception):
    class ExceptionType(Enum):
        UNKNOWN_ERROR = 500
        DB_ERROR = 500
        MISSING_REQUIRED_PARAMETERS = 400
        UNAUTHORIZED = 401
        PAGE_NOT_FOUND = 404
        METHOD_NOT_ALLOWED = 405
        MODULE_LOCK=403

    def __init__(self, exception_type: ExceptionType = None,
                 status_id=None, message=""):
        if status_id and message:
            self.status_id = status_id
            self.message = message
        elif exception_type is not None:
            self.status_id = exception_type.value
            self.message = prateek_gupta.configuration_properties["exception_messages"].get(
                exception_type.name)
        elif message:
            self.message = message
            self.status_id = ServiceException.ExceptionType.UNKNOWN_ERROR.value
        else:
            self.status_id = ServiceException.ExceptionType.UNKNOWN_ERROR.value
            self.message = prateek_gupta.configuration_properties["exception_messages"].get(
                ServiceException.ExceptionType.UNKNOWN_ERROR.name)

        super().__init__(self.message)


def log_error():
    # Logging the exception
    logger.error(traceback.format_exc())

    # Sending email to the Manager
    # if mail_error:
    #     email_subject = 'Error!!'
    #     email_message = ('Please have a look at the following error<br><br> '
    #                      '<div style="color:red;">' +
    #                      str(traceback.format_exc()).replace("\n", " <br> ") +
    #                      '</div>')
    #     from util import send_email
    #     send_email(email_subject, html_body=email_message)

def module_lock_check(field_key:str,field_value:str):
    from prateek_gupta import configuration_properties
    config_value = configuration_properties.get(field_key, None)
    if not config_value or config_value != field_value:
        raise ServiceException(exception_type=ServiceException.ExceptionType.MODULE_LOCK)