import asyncio
import mimetypes
import os
import sys
from urllib.parse import urljoin

import javaproperties
import jwt
from asgiref.sync import sync_to_async

from utils import get_success_response, get_error_response


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


async def load_properties_from_file(
        file_path, required_fields, expected_fields, fetch_all):
    properties_holder = dict()
    # noinspection PyBroadException
    try:
        missing_fields = list()

        # Check if the config file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Config file not found at: {file_path}")

        with open(file_path, 'r') as file:
            properties = javaproperties.load(file)

        if fetch_all:
            for field in properties.keys():
                properties_holder[field] = properties.get(field, '')
        else:
            for field in required_fields:
                properties_holder[field] = properties.get(field, '')
                if not properties_holder[field]:
                    missing_fields.append(field)

            if missing_fields:
                raise ValueError(
                    (f"{'These' if len(missing_fields) > 1 else 'This'} "
                     f"properties are missing: {', '.join(missing_fields)}.")
                )

            for field in expected_fields:
                properties_holder[field] = properties.get(field, "")

    except Exception as e:
        print(e)
        sys.exit(0)

    return properties_holder


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
                return get_error_response(e)

        return updated_view

    return request_mapping_args


async def async_iterator(data):
    yield data


@sync_to_async
def execute_as_async(method, *args, **kwargs):
    return method(*args, **kwargs)


def build_url(relative_url):
    from prateek_gupta import configuration_properties
    context_path = configuration_properties.get('context_path', '')
    base_url = configuration_properties.get('base_url', '')
    return urljoin(base_url, context_path + "/" + relative_url) if relative_url else ""


def get_content_type(file_name):
    content_type, _ = mimetypes.guess_type(file_name)

    if content_type:
        maintype, subtype = content_type.split("/", 1)
    else:
        maintype, subtype = "application", "octet-stream"

    return {"maintype": maintype, "subtype": subtype,"content_type": content_type}
