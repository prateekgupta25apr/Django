from prateek_gupta.LogManager import logger
from prateek_gupta.exceptions import ServiceException
from prateek_gupta.redis_async import get_value, upsert, search_keys, delete_value
from prateek_gupta.utils import request_mapping
from utils import get_success_response, get_error_response, get_api_response


@request_mapping("GET")
async def get_request(request):
    logger.info("Entering get_request()")
    # noinspection PyBroadException
    try:
        from prateek_gupta import configuration_properties, module_lock_message
        enable_redis = configuration_properties.get("REDIS_ENABLE", None)
        if enable_redis and enable_redis == "A":
            key = request.GET.get("key", "")
            use_map:str = request.GET.get("useMap", "")
            value = await get_value(key, use_map.lower() == "true")
            response = get_success_response({
                "message": "Successfully fetched the value", "value": value})
        else:
            response=get_api_response({"message":module_lock_message},403)
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing get_request()")
    return response


@request_mapping("POST")
async def upsert_request(request):
    logger.info("Entering upsert_request()")
    # noinspection PyBroadException
    try:
        from prateek_gupta import configuration_properties, module_lock_message
        enable_redis = configuration_properties.get("REDIS_ENABLE", None)
        if enable_redis and enable_redis == "A":
            key = request.POST.get("key", "")
            value = request.POST.get("value", "")
            use_map: str = request.POST.get("useMap", "")
            await upsert(key, value, use_map.lower() == "true")
            response = get_success_response({"message": "Successfully saved the value"})
        else:
            response=get_api_response({"message":module_lock_message},403)
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing upsert_request()")
    return response


@request_mapping("POST")
async def search_keys_request(request):
    logger.info("Entering search_keys_request()")
    # noinspection PyBroadException
    try:
        from prateek_gupta import configuration_properties, module_lock_message
        enable_redis = configuration_properties.get("REDIS_ENABLE", None)
        if enable_redis and enable_redis == "A":
            pattern = request.POST.get("pattern", "")
            matches = await search_keys(pattern)
            response = get_success_response({
                "message": "Successfully found the keys", "data": matches})
        else:
            response=get_api_response({"message":module_lock_message},403)
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing search_keys_request()")
    return response


@request_mapping("DELETE")
async def delete_request(request):
    logger.info("Entering delete_request()")
    # noinspection PyBroadException
    try:
        from prateek_gupta import configuration_properties, module_lock_message
        enable_redis = configuration_properties.get("REDIS_ENABLE", None)
        if enable_redis and enable_redis == "A":
            key = request.GET.get("key", "")
            use_map: str = request.GET.get("useMap", "")
            await delete_value(key, use_map.lower() == "true")
            response = get_success_response({"message": "Successfully deleted the value"})
        else:
            response=get_api_response({"message":module_lock_message},403)
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing delete_request()")
    return response
