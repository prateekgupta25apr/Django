import json

from django.http import FileResponse
from django.http.multipartparser import MultiPartParser

from prateek_gupta.LogManager import logger
from db.db_sync import (get_data, save_data, update_data,
                        partial_update_data, delete_data, add_attachment, get_attachment_path)
from prateek_gupta.aws_sync import get_file_content_in_bytes, get_file_details
from prateek_gupta.exceptions import ServiceException
from prateek_gupta.utils import request_mapping, async_iterator
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
def save_data_request(request):
    logger.info("Entering save_data_request()")
    # noinspection PyBroadException
    try:
        data = request.body
        if data:
            data = json.loads(data)
        else:
            raise ServiceException(
                exception_type=ServiceException.ExceptionType.MISSING_REQUIRED_PARAMETERS)
        save_data(data)
        response = get_success_response({"message": "Data saved successfully"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing save_data_request()")
    return response


@request_mapping("PUT")
def update_data_request(request):
    logger.info("Entering update_data_request()")
    # noinspection PyBroadException
    try:
        parser = MultiPartParser(request.META, request, request.upload_handlers)
        payload, _ = parser.parse()
        primary_key = payload.get("primary_key", None)
        col_1 = payload.get("col_1", None)
        col_2 = payload.get("col_2", None)
        update_data(primary_key, col_1, col_2)
        response = get_success_response({"message": "Data updated successfully"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing update_data_request()")
    return response


@request_mapping("PATCH")
def partial_update_data_request(request):
    logger.info("Entering update_data()")
    # noinspection PyBroadException
    try:
        parser = MultiPartParser(request.META, request, request.upload_handlers)
        payload, _ = parser.parse()
        primary_key = payload.get("primary_key", None)
        col_1 = payload.get("col_1", None)
        col_2 = payload.get("col_2", None)

        if col_1 is not None or col_2 is not None:
            partial_update_data(primary_key, col_1, col_2)
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
def delete_data_request(request, primary_key):
    logger.info("Entering delete_data_request()")
    # noinspection PyBroadException
    try:
        delete_data(primary_key)
        response = get_success_response({"message": "Data deleted successfully"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing delete_data_request()")
    return response


@request_mapping("POST")
def add_attachment_request(request):
    logger.info("Entering add_attachment_request()")
    # noinspection PyBroadException
    try:
        attachment = request.FILES['attachment']
        table_1_primary_key = request.POST.get('table_1_primary_key', "")
        add_attachment(table_1_primary_key, attachment)
        response = get_success_response({"message": "Attachment added successfully"})
    except ServiceException as e:
        response = get_error_response(e, request=request)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing add_attachment_request()")
    return response


@request_mapping("GET")
def get_attachment_request(request):
    # noinspection PyBroadException
    try:
        primary_key: str = request.GET.get("primaryKey")
        file_name: str = get_attachment_path(primary_key)
        file_content = get_file_content_in_bytes(file_name)

        # Setting opened file as content for the response
        file_details = get_file_details(file_name)

        # Using async_iterator() because the environment is async
        response = FileResponse(
            async_iterator(file_content),
            content_type=file_details.get('ContentType', 'application/octet-stream'))

        # Setting "Content-Disposition" header for the response to trigger download
        downloaded_file_name = file_name.split("/")[-1]
        response['Content-Disposition'] = f'inline; filename={downloaded_file_name}'

        # Returning response
        return response
    except ServiceException as e:
        return get_error_response(e, request=request)
    except Exception:
        return get_error_response(ServiceException())

