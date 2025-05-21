import asyncio
import os
import sys

import django
import javaproperties
import jwt
from asgiref.sync import sync_to_async
from django.db import connections, transaction

from utils import get_success_response
import mysql.connector


def process_cookie(decode, secret_key, cookie="",
                   cookie_data=None,
                   algorithms=None):
    if cookie_data is None:
        cookie_data = {}
    if algorithms is None:
        algorithms = ["HS512"]

    if decode:
        if cookie:
            cookie_data = jwt.decode(cookie, secret_key, algorithms)
        else:
            cookie_data = dict()
        result = cookie_data
    else:
        if cookie_data:
            cookie = jwt.encode(cookie_data, secret_key, algorithms[0])
        else:
            cookie = ""
        result = cookie
    return result


async def load_config_value(file_path, config_properties,
                            required_fields,
                            expected_fields):
    # noinspection PyBroadException
    try:
        missing_fields = list()

        # Check if the config file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Config file not found at: {file_path}")

        with open(file_path, 'r') as file:
            properties = javaproperties.load(file)

        for field in required_fields:
            config_properties[field] = properties.get(field, '')
            if not config_properties[field]:
                missing_fields.append(field)

        if missing_fields:
            raise ValueError(
                (f"{'These' if len(missing_fields) > 1 else 'This'} properties are missing: "
                 f"{', '.join(missing_fields)}.")
            )

        for field in expected_fields:
            config_properties[field] = properties.get(field, "")

    except Exception as e:
        print(e)
        sys.exit(0)


def request_mapping(method_name):
    def request_mapping_args(view_name):
        async def updated_view(request, *args, **kwargs):
            from prateek_gupta.exceptions import ServiceException
            try:
                if request.method == 'OPTIONS':
                    if request.method == "OPTIONS":
                        return get_success_response({"message": "Success"})

                if request.method != method_name:
                    raise (ServiceException(
                        ServiceException.ExceptionType.METHOD_NOT_ALLOWED))

                if asyncio.iscoroutinefunction(view_name):
                    return await view_name(request, *args, **kwargs)
                else:
                    return view_name(request, *args, **kwargs)
            except ServiceException as e:
                return e.get_error_response()

        return updated_view

    return request_mapping_args


async def async_iterator(data):
    yield data


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
                user=configuration_properties['db_user'],
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


@sync_to_async
def execute_as_async(method, *args, **kwargs):
    return method(*args, **kwargs)
