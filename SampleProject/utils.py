import json

from asgiref.sync import sync_to_async
from django.http import HttpResponse
from django.db import connections, transaction
import mysql.connector
import django


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


@sync_to_async
def execute_query(query, method=None, thread_execution=None):
    # noinspection PyBroadException
    try:
        if not thread_execution:
            try:
                connection = connections['default']

                with transaction.atomic():
                    with connection.cursor() as cursor:
                        result = cursor.execute(query)

                        if method == 'fetchone':
                            result = cursor.fetchone()
                        elif method == 'fetchall':
                            result = cursor.fetchall()

                return result
            except django.db.utils.OperationalError:
                from prateek_gupta import exceptions
                exceptions.log_error()
                from prateek_gupta.LogManager import logger
                logger.info(f"DB_EXECUTION_ERROR: Executing query with new connection")
                return execute_thread_query(query, method)
        else:
            return execute_thread_query(query, method)
    except Exception as e:
        from prateek_gupta import exceptions
        exceptions.log_error()
        raise e


def execute_thread_query(query, method=None):
    try:
        from prateek_gupta import exceptions, configuration_properties
        with (mysql.connector.connect(
                host=configuration_properties['db_host'],
                user=configuration_properties['db_user_name'],
                password=configuration_properties['db_password']) as
        manual_connection):
            with manual_connection.cursor() as manual_cursor:
                manual_cursor.execute(query)

                if method == 'fetchone':
                    result = manual_cursor.fetchone()
                elif method == 'fetchall':
                    result = manual_cursor.fetchall()
                else:
                    result = manual_cursor.rowcount
                    manual_connection.commit()

                return result

    except mysql.connector.Error as e:
        from prateek_gupta import exceptions
        exceptions.log_error()
        from prateek_gupta.LogManager import logger
        logger.info(f"DB_EXECUTION_ERROR: Even manual connection failed")
        raise e


def validate_user_login(request):
    from prateek_gupta.exceptions import ServiceException
    if request.user_context.user_id <= 0:
        raise ServiceException(exception_type=ServiceException.ExceptionType.LOGIN_REQUIRED)

