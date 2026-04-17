from django.http.multipartparser import MultiPartParser

from prateek_gupta.exceptions import ServiceException, module_lock_check
from prateek_gupta.sqs_sync import (
    get_all_queues, send_message, create_queue, get_queue, update_queue,
    delete_queue, update_queues, get_messages
)
from prateek_gupta.utils import (request_mapping)
from utils import (get_success_response, get_error_response)


@request_mapping("POST")
def send_message_request(request):
    # noinspection PyBroadException
    try:
        module_lock_check("SQS_ENABLE", "S")
        queue_name = request.POST.get('queue_name')
        message = request.POST.get('message')
        result = send_message(queue_name, message)
        response = dict()
        response['message'] = result
        response = get_success_response(response)

    except ServiceException as e:
        response = get_error_response(e, request=request)
    except Exception:
        response = get_error_response(ServiceException())
    return response


@request_mapping("GET")
def get_all_queues_request(request):
    # noinspection PyBroadException
    try:
        module_lock_check("SQS_ENABLE", "S")
        response = dict()
        response['queues'] = get_all_queues()
        response = get_success_response(response)

    except ServiceException as e:
        response = get_error_response(e, request=request)
    except Exception:
        response = get_error_response(ServiceException())
    return response


@request_mapping("GET")
def get_queue_request(request):
    # noinspection PyBroadException
    try:
        module_lock_check("SQS_ENABLE", "S")
        queue_name = request.GET.get('queue_name')
        response = dict()
        response['queue_details'] = get_queue(queue_name)
        response = get_success_response(response)

    except ServiceException as e:
        response = get_error_response(e, request=request)
    except Exception:
        response = get_error_response(ServiceException())
    return response


@request_mapping("POST")
def create_queue_request(request):
    # noinspection PyBroadException
    try:
        module_lock_check("SQS_ENABLE", "S")
        queue_name = request.POST.get('queue_name')
        visibility_timeout = request.POST.get('visibility_timeout', "30")
        retention_period = request.POST.get('retention_period', "86400")
        create_queue(queue_name, visibility_timeout, retention_period)
        response = dict()
        response['message'] = "Queue created successfully"
        response = get_success_response(response)

    except ServiceException as e:
        response = get_error_response(e, request=request)
    except Exception as e:
        response = get_error_response(e)
    return response


@request_mapping("PUT")
def update_queue_request(request):
    # noinspection PyBroadException
    try:
        module_lock_check("SQS_ENABLE", "S")
        parser = MultiPartParser(request.META, request, request.upload_handlers)
        payload, _ = parser.parse()
        queue_name = payload.get('queue_name')
        attribute_name = payload.get('attribute_name', None)
        attribute_value = payload.get('attribute_value', None)
        update_queue(queue_name, attribute_name, attribute_value)
        response = dict()
        response['message'] = "Queue updated successfully"
        response = get_success_response(response)

    except ServiceException as e:
        response = get_error_response(e, request=request)
    except Exception as e:
        response = get_error_response(e)
    return response


@request_mapping("DELETE")
def delete_queue_request(request):
    # noinspection PyBroadException
    try:
        module_lock_check("SQS_ENABLE", "S")
        queue_name = request.GET.get('queue_name')
        delete_queue(queue_name)
        response = dict()
        response['message'] = "Queue deleted successfully"
        response = get_success_response(response)

    except ServiceException as e:
        response = get_error_response(e, request=request)
    except Exception as e:
        response = get_error_response(e)
    return response


@request_mapping("POST")
def add_queue_request(request):
    # noinspection PyBroadException
    try:
        module_lock_check("SQS_ENABLE", "S")

        queue_name = request.POST.get("queue_name", "")
        update_queues(queue_name, True)
        response = get_success_response({"message": "Successfully added queue"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    return response


@request_mapping("POST")
def remove_queue_request(request):
    # noinspection PyBroadException
    try:
        module_lock_check("SQS_ENABLE", "S")

        queue_name = request.POST.get("queue_name", "")
        update_queues(queue_name, False)
        response = get_success_response({"message": "Successfully removed queue"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    return response


@request_mapping("GET")
def get_messages_request(request):
    # noinspection PyBroadException
    try:
        module_lock_check("SQS_ENABLE", "S")
        queue_name = request.GET.get('queue_name')
        response = dict()
        response['messages'] = get_messages(queue_name)
        response = get_success_response(response)

    except ServiceException as e:
        response = get_error_response(e, request=request)
    except Exception:
        response = get_error_response(ServiceException())
    return response
