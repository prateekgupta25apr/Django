import json

from django.http import HttpResponse


def get_api_response(body,status):
    """Method to return generic JSON response for an API"""
    try:
        if type(body) in [dict, list]:
            response = json.dumps(body)
        else:
            response = body
        return HttpResponse(response, content_type="application/json", status=status)
    except Exception as e:
        print(str(e))


def get_success_response(body):
    """Method to return generic JSON response for an API"""
    return get_api_response(body,200)


def get_error_response(exception, request=None):
    """Method to return response for errors"""
    from prateek_gupta.LogManager import logger
    from prateek_gupta.exceptions import log_error, ServiceException
    exception: ServiceException=exception

    # Logging error
    log_error()

    if request is not None:
        logger.error("Error while responding the api : "+request.path)

    response = dict()
    if exception.status_id is not None:
        response["message"] = exception.message
        return get_api_response(response,exception.status_id)
    else:
        response["message"] = exception.message
        return get_api_response(response,
                                ServiceException.ExceptionType.UNKNOWN_ERROR.value)

