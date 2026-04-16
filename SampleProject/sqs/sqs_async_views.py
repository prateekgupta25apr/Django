from prateek_gupta.exceptions import ServiceException, module_lock_check
from prateek_gupta.sqs_sync import get_all_queues, send_message
from prateek_gupta.utils import (request_mapping)
from utils import (get_success_response, get_error_response)


@request_mapping("GET")
def get_all_queues_request(request):
    # noinspection PyBroadException
    try:
        module_lock_check("SQS_ENABLE", "S")
        response=dict()
        response['queues'] = get_all_queues()
        response = get_success_response(response)

    except ServiceException as e:
        response = get_error_response(e,request=request)
    except Exception:
        response = get_error_response(ServiceException())
    return response


@request_mapping("POST")
def send_message_request(request):
    # noinspection PyBroadException
    try:
        module_lock_check("SQS_ENABLE", "S")
        queue_name = request.POST.get('queue_name')
        message = request.POST.get('message')
        result=send_message(queue_name, message)
        response=dict()
        response['message'] = result
        response = get_success_response(response)

    except ServiceException as e:
        response = get_error_response(e,request=request)
    except Exception:
        response = get_error_response(ServiceException())
    return response
