import traceback
from enum import Enum

from prateek_gupta import configuration_properties
from prateek_gupta.LogManager import logger
from utils import get_api_response


class ServiceException(BaseException):
    class ExceptionType(Enum):
        UNKNOWN_ERROR = 500
        DB_ERROR=500
        MISSING_REQUIRED_PARAMETERS = 400
        UNAUTHORIZED=401
        PAGE_NOT_FOUND = 404
        METHOD_NOT_ALLOWED = 405



    def __init__(self, exception_type:ExceptionType=None,
                 status_id=None, message=""):
        if status_id and message:
            self.status_id=status_id
            self.message=message
        elif exception_type is not None:
            self.status_id = exception_type.value
            self.message = configuration_properties["exception_messages"].get(
                exception_type.name)
        elif message:
            self.message=message
            self.status_id=ServiceException.ExceptionType.UNKNOWN_ERROR.value
        else:
            self.status_id=ServiceException.ExceptionType.UNKNOWN_ERROR.value
            self.message = configuration_properties["exception_messages"].get(
                ServiceException.ExceptionType.UNKNOWN_ERROR.name)

        super().__init__(self.message)


def log_error():
    # Logging the exception
    logger.error(traceback.format_exc())
