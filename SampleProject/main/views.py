from django.conf import settings
from django.http import HttpResponse

from prateek_gupta import get_api_response
from prateek_gupta.LogManager import logger
from prateek_gupta.exceptions import ServiceException


async def test(request):
    logger.info("Entering test()")
    # noinspection PyBroadException
    try:
        response = get_api_response({"message":"Success"}, 200)
    except ServiceException as e:
        response = e.get_error_response()
    except Exception:
        response = (ServiceException(error_id=ServiceException.UNKNOWN_ERROR)
                    .get_error_response())
    logger.info("Exiting github_add_comment()")
    return response
