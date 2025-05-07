from prateek_gupta.LogManager import logger
from prateek_gupta.exceptions import ServiceException
from prateek_gupta.utils import execute_query
from utils import get_api_response


async def test(request):
    logger.info("Entering test()")
    # noinspection PyBroadException
    try:
        result= await execute_query("select schema();",'fetchone')
        response = get_api_response({"message":"Success","result":result}, 200)
    except ServiceException as e:
        response = e.get_error_response()
    except Exception:
        response = (ServiceException(error_id=ServiceException.UNKNOWN_ERROR)
                    .get_error_response())
    logger.info("Exiting test()")
    return response
