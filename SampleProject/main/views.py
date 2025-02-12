from prateek_gupta.LogManager import logger
from prateek_gupta.exceptions import ServiceException
from prateek_gupta.utils import get_api_response


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
