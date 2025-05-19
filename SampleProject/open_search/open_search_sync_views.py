from prateek_gupta.LogManager import logger
from prateek_gupta.exceptions import ServiceException
from prateek_gupta.open_search_sync import get_index
from prateek_gupta.utils import request_mapping
from utils import get_success_response


@request_mapping("GET")
def get_index_request(request):
    logger.info("Entering get_index_request()")
    # noinspection PyBroadException
    try:
        index_name = request.GET.get("indexName")
        response = get_success_response({
            "message": "Index details fetched successfully",
            "details": get_index(index_name)})
    except ServiceException as e:
        response = e.get_error_response()
    except Exception:
        response = ServiceException().get_error_response()
    logger.info("Existing get_index_request()")
    return response
