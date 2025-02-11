import aioboto3
from aiobotocore.config import AioConfig
from django.http import FileResponse

import prateek_gupta
from SampleProject.settings import AWS_STORAGE_BUCKET_NAME
from prateek_gupta.exceptions import *
from prateek_gupta.LogManager import logger
from prateek_gupta import (get_success_response, request_mapping,get_api_response)


async def get_s3_client(user_cred=None,cred_config:dict=None):
    if user_cred is None:
        user_cred= prateek_gupta.local_run
    logger.info("Entering get_s3_client()")
    session = aioboto3.Session()
    creds = await session.get_credentials()
    creds=await creds.get_frozen_credentials()
    config = AioConfig(signature_version="s3v4")
    async with session.client('s3',config=config) as s3_client:
        if s3_client is None or user_cred:
            if all(cred_config[field] for field in
                    ['AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY','AWS_S3_REGION_NAME']):
                logger.info("Static : Access Key : "+
                            cred_config['AWS_ACCESS_KEY_ID']+
                            " ; Secret Key "+
                            cred_config['AWS_SECRET_ACCESS_KEY'])

                async with session.client(
                    's3',
                    aws_access_key_id=cred_config['AWS_ACCESS_KEY_ID'],
                    aws_secret_access_key=cred_config['AWS_SECRET_ACCESS_KEY'],
                    region_name=cred_config['AWS_S3_REGION_NAME'],
                ) as s3_client_obj:
                    s3_client=s3_client_obj
            else:
                logger.info("Configs AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY or "
                            "AWS_S3_REGION_NAME are not properly configured")
                s3_client=None
        else:
            logger.info("Dynamic : Access Key : " + creds.access_key +
                        " ; Secret Key " + creds.secret_key)

    logger.info("Existing get_s3_client()")
    return s3_client

def get_bucket_name(default=False):
    # noinspection PyBroadException
    try:
        if default:
            bucket_name = "pg"
        else:
            bucket_name= AWS_STORAGE_BUCKET_NAME
        logger.info("Bucket Name : "+bucket_name)
    except Exception:
        log_error()
        bucket_name=None
    return bucket_name

async def get_file_content_in_bytes(file_name=None,
                                    request=None):
    # noinspection PyBroadException
    try:
        if file_name is None:
            raise ServiceException(message="Valid file name not passed")

        response_in_bytes=None
        s3_client = await get_s3_client()
        async with s3_client as s3_client:
            if s3_client is None:
                raise ServiceException(
                    message="Couldn't establish a connection to AWS")

            bucket_name=get_bucket_name(request)
            if not bucket_name:
                raise ServiceException(message="Couldn't get bucket name")

            response = await s3_client.get_object(Bucket=bucket_name, Key=file_name)

            response_in_bytes = await response['Body'].read()

    except ServiceException:
        Utils.exceptions.log_error()
        response_in_bytes=None
    except Exception:
        Utils.exceptions.log_error()
        response_in_bytes=None
    return response_in_bytes

@request_mapping("POST")
async def upload_file_request(request):
    logger.info("Entering upload_file_request()")
    # noinspection PyBroadException
    try:
        file=request.FILES['file']

        bucket_name = get_bucket_name(request)

        if not bucket_name:
            raise ServiceException(message="Couldn't get bucket name")

        await upload_file(bucket_name, file)
        response=dict()
        response['message']="Successfully uploaded the file : "+file.name
        response=get_success_response(response)
    except Exception :
        response=ServiceException().get_error_response()
    logger.info("Existing upload_file_request()")
    return response

async def upload_file(bucket_name,file,prefix=""):
    logger.info("Entering upload_file()")
    s3_client = await get_s3_client()
    async with s3_client as s3_client:
        if s3_client is None:
            raise ServiceException(
                message="Couldn't establish a connection to AWS")

        await s3_client.upload_fileobj(file, bucket_name, (prefix+file.name),
                                       ExtraArgs={'ContentType': file.content_type})
    logger.info("Exiting upload_file()")

@request_mapping("DELETE")
async def delete_file(request):
    logger.info("Entering delete_file()")
    # noinspection PyBroadException
    try:
        file_name=request.GET['file_name']

        bucket_name = get_bucket_name(request)

        if not bucket_name:
            raise ServiceException(message="Couldn't get bucket name")

        s3_client = await get_s3_client()
        async with s3_client as s3_client:
            if s3_client is None:
                raise ServiceException(
                    message="Couldn't establish a connection to AWS")

            await s3_client.delete_object(Bucket=bucket_name,Key=file_name)
        response=dict()
        response['message']="Successfully delete the file : "+file_name
        response=get_success_response(response)
    except Exception :
        Utils.exceptions.log_error()
        response=ServiceException().get_error_response()
    logger.info("Existing delete_file()")
    return response

@request_mapping("GET")
async def get_file(request):
    # noinspection PyBroadException
    try:
        # Fetch the file from S3
        file_key = request.GET.get('file_name')

        bucket_name = get_bucket_name(request)
        if not bucket_name:
            raise ServiceException(message="Couldn't get bucket name")

        s3_client = await get_s3_client()
        async with s3_client as s3_client:
            if s3_client is None:
                raise ServiceException(
                    message="Couldn't establish a connection to AWS")

            # Fetch file from S3
            # noinspection PyBroadException
            try:
                await s3_client.head_object(Bucket=bucket_name, Key=file_key)
                file_response = await s3_client.get_object(Bucket=bucket_name, Key=file_key)
                file_content = await file_response['Body'].read()
                response = FileResponse(async_iterator(file_content))
                response['Content-Disposition'] = 'attachment; filename=' + file_key
            except Exception:
                Utils.exceptions.log_error()
                response=get_api_response({"message":"File not found"},400)
    except Exception:
        Utils.exceptions.log_error()
        response=ServiceException().get_error_response()
    return response

@request_mapping("GET")
async def get_pre_signed_url(request):
    # noinspection PyBroadException
    try:
        # Fetch the file from S3
        file_key = request.GET.get('file_name')

        bucket_name = get_bucket_name(request)
        if not bucket_name:
            raise ServiceException(message="Couldn't get bucket name")

        s3_client = await get_s3_client()
        async with s3_client as s3_client:
            if s3_client is None:
                raise ServiceException(
                    message="Couldn't establish a connection to AWS")

            # Fetch file from S3
            # noinspection PyBroadException
            try:
                await s3_client.head_object(Bucket=bucket_name, Key=file_key)

                url = await s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name, 'Key': file_key})
                response=get_success_response(
                    {"message":"Generated pre-signed url successfully",
                     "Pre-Signed URL":url})
            except Exception:
                Utils.exceptions.log_error()
                response=get_api_response({"message":"File not found"},400)
    except Exception:
        Utils.exceptions.log_error()
        response=ServiceException().get_error_response()
    return response