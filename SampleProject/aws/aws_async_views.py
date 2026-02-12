from django.http import FileResponse

from prateek_gupta.aws_async import *
from prateek_gupta.exceptions import ServiceException
from prateek_gupta.utils import (request_mapping, async_iterator)
from utils import (get_success_response, get_api_response, get_error_response)


@request_mapping("GET")
async def get_file(request):
    # noinspection PyBroadException
    try:
        module_lock_check("AWS_ENABLE", "A")

        file_key = request.GET.get('file_name')
        if await check_file_existence(file_key):
            file_content = await get_file_content_in_bytes(file_key)
            response = FileResponse(async_iterator(file_content))
            response['Content-Disposition'] = 'attachment; filename=' + file_key
        else:
            response = get_api_response({"message": "File not found"}, 400)
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    return response


@request_mapping("POST")
async def upload_file(request):
    logger.info("Entering upload_file()")
    # noinspection PyBroadException
    try:
        module_lock_check("AWS_ENABLE", "A")

        file = request.FILES['file']
        prefix = request.POST.get('prefix', "")
        file_key = update_file_name(file.name, prefix)
        await upload(file, file_key=file_key)
        response = dict()
        response['message'] = "Successfully uploaded the file : " + file.name
        response['file_name'] = file.name
        response['file_key'] = file_key
        response['pre_signed_url'] = await pre_signed_url(file_key, None)
        response = get_success_response(response)
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing upload_file()")
    return response


@request_mapping("DELETE")
async def delete_file(request):
    logger.info("Entering delete_file()")
    # noinspection PyBroadException
    try:
        module_lock_check("AWS_ENABLE", "A")

        file_name = request.GET['file_name']

        await delete(file_name)
        response = dict()
        response['message'] = "Successfully delete the file : " + file_name
        response = get_success_response(response)
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing delete_file()")
    return response


@request_mapping("GET")
async def get_pre_signed_url(request):
    # noinspection PyBroadException
    try:
        module_lock_check("AWS_ENABLE", "A")

        file_key = request.GET.get('file_name')
        method = request.GET.get('method', None)

        url = await pre_signed_url(file_key, method)
        response = get_success_response({
            "message": "Generated pre-signed url successfully",
            "Pre-Signed URL": url
        })

    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    return response


@request_mapping("POST")
async def extract_file_name_request(request):
    # noinspection PyBroadException
    try:
        module_lock_check("AWS_ENABLE", "A")

        file_path = request.POST.get('file_path')

        file_name = extract_file_name(file_path,True)
        response = get_success_response({
            "message": "Extracted file name successfully",
            "file_name": file_name
        })

    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    return response
