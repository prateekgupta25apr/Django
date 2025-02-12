from django.http import FileResponse


from prateek_gupta.aws_async import *
from prateek_gupta.exceptions import ServiceException, log_error
from prateek_gupta.utils import (get_success_response, request_mapping, async_iterator,
                                 get_api_response)


@request_mapping("GET")
async def get_file(request):
    # noinspection PyBroadException
    try:
        file_key = request.GET.get('file_name')
        if await check_file_existence(file_key):
            file_content = await get_file_content_in_bytes(file_key)
            response = FileResponse(async_iterator(file_content))
            response['Content-Disposition'] = 'attachment; filename=' + file_key
        else:
            response = get_api_response({"message": "File not found"}, 400)
    except ServiceException as e:
        response = e.get_error_response()
    except Exception:
        response=ServiceException().get_error_response()
    return response

@request_mapping("POST")
async def upload_file(request):
    logger.info("Entering upload_file()")
    # noinspection PyBroadException
    try:
        file=request.FILES['file']

        bucket_name = get_bucket_name()

        if not bucket_name:
            raise ServiceException(message="Couldn't get bucket name")

        await upload(bucket_name, file)
        response=dict()
        response['message']="Successfully uploaded the file : "+file.name
        response=get_success_response(response)
    except ServiceException as e:
        response = e.get_error_response()
    except Exception:
        response = ServiceException().get_error_response()
    logger.info("Existing upload_file()")
    return response

@request_mapping("DELETE")
async def delete_file(request):
    logger.info("Entering delete_file()")
    # noinspection PyBroadException
    try:
        file_name=request.GET['file_name']

        await delete(file_name)
        response=dict()
        response['message']="Successfully delete the file : "+file_name
        response=get_success_response(response)
    except ServiceException as e:
        response = e.get_error_response()
    except Exception:
        response = ServiceException().get_error_response()
    logger.info("Existing delete_file()")
    return response

@request_mapping("GET")
async def get_pre_signed_url(request):
    # noinspection PyBroadException
    try:
        # Fetch the file from S3
        file_key = request.GET.get('file_name')

        url = await pre_signed_url(file_key)
        response=get_success_response({"message":"Generated pre-signed url successfully",
                     "Pre-Signed URL":url})

    except ServiceException as e:
        response = e.get_error_response()
    except Exception:
        response = ServiceException().get_error_response()
    return response