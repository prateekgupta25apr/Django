import json

from django.http.multipartparser import MultiPartParser

from prateek_gupta.LogManager import logger
from prateek_gupta.db_sync import (get_data, save_data, update_data,
                                    partial_update_data, delete_data)
from prateek_gupta.exceptions import ServiceException
from prateek_gupta.utils import request_mapping
from utils import get_success_response, get_error_response


@request_mapping('GET')
def get_data_request(request):
    logger.info("Entering get_data_request()")
    # noinspection PyBroadException
    try:
        primary_key = request.GET.get("primary_key", None)
        result_list = get_data(primary_key)
        response = get_success_response({"data": result_list})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing get_data_request()")
    return response


@request_mapping("POST")
async def save_data_request(request):
    logger.info("Entering save_data_request()")
    # noinspection PyBroadException
    try:
        data = request.body
        if data:
            data = json.loads(data)
        else:
            raise ServiceException(
                exception_type=ServiceException.ExceptionType.MISSING_REQUIRED_PARAMETERS)
        await save_data(data)
        response = get_success_response({"message": "Data saved successfully"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing save_data_request()")
    return response


@request_mapping("PUT")
async def update_data_request(request):
    logger.info("Entering update_data_request()")
    # noinspection PyBroadException
    try:
        parser = MultiPartParser(request.META, request, request.upload_handlers)
        payload, _ = parser.parse()
        primary_key = payload.get("primary_key", None)
        col_1 = payload.get("col_1", None)
        col_2 = payload.get("col_2", None)
        await update_data(primary_key, col_1, col_2)
        response = get_success_response({"message": "Data updated successfully"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing update_data_request()")
    return response


@request_mapping("PATCH")
async def partial_update_data_request(request):
    logger.info("Entering update_data()")
    # noinspection PyBroadException
    try:
        parser = MultiPartParser(request.META, request, request.upload_handlers)
        payload, _ = parser.parse()
        primary_key = payload.get("primary_key", None)
        col_1 = payload.get("col_1", None)
        col_2 = payload.get("col_2", None)

        if col_1 is not None or col_2 is not None:
            await partial_update_data(primary_key, col_1, col_2)
            response = get_success_response({"message": "Data updated successfully"})
        else:
            raise ServiceException(
                exception_type=ServiceException.ExceptionType.MISSING_REQUIRED_PARAMETERS)
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing update_data()")
    return response


@request_mapping("DELETE")
async def delete_data_request(request, primary_key):
    logger.info("Entering delete_data_request()")
    # noinspection PyBroadException
    try:
        await delete_data(primary_key)
        response = get_success_response({"message": "Data deleted successfully"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing delete_data_request()")
    return response
