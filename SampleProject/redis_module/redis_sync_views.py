from prateek_gupta.LogManager import logger
from prateek_gupta.exceptions import ServiceException
from prateek_gupta.redis_sync import get_value, upsert, search_keys, delete_value
from prateek_gupta.utils import request_mapping
from utils import get_success_response, get_error_response


@request_mapping("GET")
def get_request(request):
    logger.info("Entering get_request()")
    # noinspection PyBroadException
    try:
        key = request.GET.get("key", "")
        use_map: str = request.GET.get("useMap", "")
        value = get_value(key, use_map.lower() == "true")
        response = get_success_response({
            "message": "Successfully fetched the value", "value": value})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing get_request()")
    return response


@request_mapping("POST")
def upsert_request(request):
    logger.info("Entering upsert_request()")
    # noinspection PyBroadException
    try:
        key = request.POST.get("key", "")
        value = request.POST.get("value", "")
        use_map: str = request.POST.get("useMap", "")
        upsert(key, value, use_map.lower() == "true")
        response = get_success_response({"message": "Successfully saved the value"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing upsert_request()")
    return response


@request_mapping("POST")
def search_keys_request(request):
    logger.info("Entering search_keys_request()")
    # noinspection PyBroadException
    try:
        pattern = request.POST.get("pattern", "")
        matches = search_keys(pattern)
        response = get_success_response({
            "message": "Successfully found the keys", "data": matches})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing search_keys_request()")
    return response


@request_mapping("DELETE")
def delete_request(request):
    logger.info("Entering delete_request()")
    # noinspection PyBroadException
    try:
        key = request.GET.get("key", "")
        use_map: str = request.GET.get("useMap", "")
        delete_value(key, use_map.lower() == "true")
        response = get_success_response({"message": "Successfully deleted the value"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing delete_request()")
    return response
