import asyncio
import os
import sys
from pathlib import Path
import javaproperties
import json
import jwt
from django.http import HttpResponse



project_dir=str(Path(__file__).resolve().parent.parent).replace("\\", "/")
if project_dir[-1]!="/":
    project_dir+="/"
console_logs=True

try:
    from . import *

    local_run = True
except ImportError:
    local_run = False

def process_cookie(decode, secret_key, cookie="",
                   cookie_data=None,
                   algorithms=None):
    if cookie_data is None:
        cookie_data = {}
    if algorithms is None:
        algorithms = ["HS512"]

    if decode:
        if cookie:
            cookie_data = jwt.decode(cookie,secret_key,algorithms)
        else:
            cookie_data=dict()
        result=cookie_data
    else:
        if cookie_data:
            cookie=jwt.encode(cookie_data, secret_key, algorithms[0])
        else:
            cookie=""
        result=cookie
    return result


async def load_config_value(file_path,config_properties,
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

def get_api_response(body,status):
    """Method to return generic JSON response for an API"""
    if type(body) is dict:
        response = json.dumps(body)
    else:
        response = body
    return HttpResponse(response, content_type="application/json", status=status)

def get_success_response(body):
    """Method to return generic JSON response for an API"""
    return get_api_response(body,200)

def request_mapping(method_name):
    def request_mapping_args(view_name):
        async def updated_view(request, *args, **kwargs):
            from prateek_gupta.exceptions import ServiceException
            try:
                if request.method=='OPTIONS':
                    if request.method == "OPTIONS":
                        return get_success_response({"message":"Success"})

                if request.method != method_name:
                    raise (ServiceException(
                        ServiceException.METHOD_NOT_ALLOWED))

                if asyncio.iscoroutinefunction(view_name):
                    return await view_name(request, *args, **kwargs)
                else:
                    return view_name(request, *args, **kwargs)
            except ServiceException as e:
                return e.get_error_response()
        return updated_view
    return request_mapping_args