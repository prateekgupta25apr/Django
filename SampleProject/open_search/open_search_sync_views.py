from django.http.multipartparser import MultiPartParser

from prateek_gupta.LogManager import logger
from prateek_gupta.exceptions import ServiceException
from prateek_gupta.open_search_sync import (
    get_index, create_index, update_index, delete_index, get_record,
    upsert_record, partial_update_record, delete_record, search_record, count_record,
    delete_by_query_record)
from prateek_gupta.utils import request_mapping
from utils import get_success_response, get_error_response


@request_mapping("GET")
def get_index_request(request):
    logger.info("Entering get_index_request()")
    # noinspection PyBroadException
    try:
        index_name = request.GET.get("indexName")
        response = get_index(index_name)
        if response is not None:
            response = get_success_response({
                "message": "Index details fetched successfully",
                "details": response})
        else:
            response = get_success_response({
                "message": "Index doesn't exists"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing get_index_request()")
    return response


@request_mapping("POST")
def create_index_request(request):
    logger.info("Entering create_index_request()")
    # noinspection PyBroadException
    try:
        index_name = request.POST.get("indexName")
        body = request.POST.get("source")
        response = create_index(index_name, body)
        if response is not None:
            response = get_success_response({
                "message": "Index created successfully"})
        else:
            response = get_success_response({
                "message": "Index exists"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing create_index_request()")
    return response


@request_mapping("PUT")
def update_index_request(request):
    logger.info("Entering update_index_request()")
    # noinspection PyBroadException
    try:
        parser = MultiPartParser(request.META, request, request.upload_handlers)
        payload, _ = parser.parse()
        index_name = payload.get("indexName")
        settings = payload.get("settings", None)
        mappings = payload.get("mappings", None)
        remove_alias = payload.get("removeAlias", None)
        add_alias = payload.get("addAlias", None)
        response = update_index(index_name, settings, add_alias, remove_alias, mappings)
        if response is not None:
            response = get_success_response({
                "message": "Index updated successfully"})
        else:
            response = get_success_response({
                "message": "Index exists"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing update_index_request()")
    return response


@request_mapping("DELETE")
def delete_index_request(request):
    logger.info("Entering delete_index_request()")
    # noinspection PyBroadException
    try:
        index_name = request.GET.get("indexName")
        response = delete_index(index_name)
        if response is not None:
            response = get_success_response({
                "message": "Index deleted successfully"})
        else:
            response = get_success_response({
                "message": "Index doesn't exists"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing delete_index_request()")
    return response


@request_mapping("GET")
def get_record_request(request):
    logger.info("Entering get_record_request()")
    # noinspection PyBroadException
    try:
        index_name = request.GET.get("indexName")
        record_id = request.GET.get("docId")
        response = get_record(index_name, record_id)
        if response is not None:
            response = get_success_response({
                "message": "Record details fetched successfully",
                "details": response})
        else:
            response = get_success_response({
                "message": "Index doesn't exists"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing get_record_request()")
    return response


@request_mapping("POST")
def upsert_record_request(request):
    logger.info("Entering upsert_record_request()")
    # noinspection PyBroadException
    try:
        index_name = request.POST.get("indexName")
        doc_id = request.POST.get("docId")
        data = request.POST.get("data")
        bulk = request.POST.get("bulk", False)
        response = upsert_record(index_name, doc_id, data, bulk)
        if response is not None:
            response = get_success_response({
                "message": "Index updated successfully",
                "details": response
            })
        else:
            response = get_success_response({
                "message": "Index doesn't exists"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing upsert_record_request()")
    return response


@request_mapping("PATCH")
def partial_update_record_request(request):
    logger.info("Entering partial_update_record_request()")
    # noinspection PyBroadException
    try:
        parser = MultiPartParser(request.META, request, request.upload_handlers)
        payload, _ = parser.parse()
        index_name = payload.get("indexName")
        doc_id = payload.get("docId")
        data = payload.get("data")
        bulk = payload.get("bulk", False)
        response = partial_update_record(index_name, doc_id, data, bulk)
        if response is not None:
            response = get_success_response({
                "message": "Index updated successfully",
                "details": response
            })
        else:
            response = get_success_response({
                "message": "Index doesn't exists"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing partial_update_record_request()")
    return response


@request_mapping("DELETE")
def delete_record_request(request):
    logger.info("Entering delete_record_request()")
    # noinspection PyBroadException
    try:
        index_name = request.GET.get("indexName")
        record_id = request.GET.get("docId")
        bulk = request.GET.get("bulk",False)
        response = delete_record(index_name, record_id,bulk)
        if response is not None:
            response = get_success_response({
                "message": "Record deleted successfully",
                "details": response})
        else:
            response = get_success_response({
                "message": "Index doesn't exists"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing delete_record_request()")
    return response


@request_mapping("POST")
def search_record_request(request):
    logger.info("Entering search_record_request()")
    # noinspection PyBroadException
    try:
        index_name = request.POST.get("indexName")
        search_json = request.POST.get("searchJSON")
        response = search_record(index_name, search_json)
        if response is not None:
            response = get_success_response({
                "message": "Index updated successfully",
                "details": response
            })
        else:
            response = get_success_response({
                "message": "Index doesn't exists"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing search_record_request()")
    return response


@request_mapping("POST")
def count_record_request(request):
    logger.info("Entering count_record_request()")
    # noinspection PyBroadException
    try:
        index_name = request.POST.get("indexName")
        search_json = request.POST.get("searchJSON")
        response = count_record(index_name, search_json)
        if response is not None:
            response = get_success_response({
                "message": "Index updated successfully",
                "details": response
            })
        else:
            response = get_success_response({
                "message": "Index doesn't exists"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing count_record_request()")
    return response


@request_mapping("POST")
def delete_by_query_record_request(request):
    logger.info("Entering delete_by_query_record_request()")
    # noinspection PyBroadException
    try:
        index_name = request.POST.get("indexName")
        search_json = request.POST.get("searchJSON")
        response = delete_by_query_record(index_name, search_json)
        if response is not None:
            response = get_success_response({
                "message": "Index updated successfully",
                "details": response
            })
        else:
            response = get_success_response({
                "message": "Index doesn't exists"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing delete_by_query_record_request()")
    return response
