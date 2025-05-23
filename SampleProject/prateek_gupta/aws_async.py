import aioboto3
from aiobotocore.config import AioConfig

import prateek_gupta
from prateek_gupta.exceptions import *

local_run = prateek_gupta.local
configuration_properties = prateek_gupta.configuration_properties


async def get_s3_client():
    logger.info("Entering get_s3_client()")
    session = aioboto3.Session()
    creds = await session.get_credentials()
    creds = await creds.get_frozen_credentials()
    config = AioConfig(signature_version="s3v4")
    async with session.client('s3', config=config) as s3_client:
        if s3_client is None or local_run:
            if all(configuration_properties[field] for field in
                   ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_S3_REGION_NAME']):
                logger.info("Static : Access Key : " +
                            configuration_properties['AWS_ACCESS_KEY_ID'] +
                            " ; Secret Key " +
                            configuration_properties['AWS_SECRET_ACCESS_KEY'])

                async with session.client(
                        's3',
                        aws_access_key_id=configuration_properties['AWS_ACCESS_KEY_ID'],
                        aws_secret_access_key=
                        configuration_properties['AWS_SECRET_ACCESS_KEY'],
                        region_name=configuration_properties['AWS_S3_REGION_NAME'],
                ) as s3_client_obj:
                    s3_client = s3_client_obj
            else:
                logger.info("Configs AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY or "
                            "AWS_S3_REGION_NAME are not properly configured")
                s3_client = None
        else:
            logger.info("Dynamic : Access Key : " + creds.access_key +
                        " ; Secret Key " + creds.secret_key)

    logger.info("Existing get_s3_client()")
    return s3_client


def get_bucket_name(default=False):
    # noinspection PyBroadException
    try:
        bucket_name = configuration_properties['AWS_STORAGE_BUCKET_NAME']

        if default or not bucket_name:
            bucket_name = "pg"

        logger.info("Bucket Name : " + bucket_name)
    except Exception:
        log_error()
        bucket_name = None
    return bucket_name


async def get_file_content_in_bytes(file_name=None):
    if file_name is None:
        raise ServiceException(message="Valid file name not passed")

    s3_client = await get_s3_client()
    async with s3_client as s3_client:
        if s3_client is None:
            raise ServiceException(
                message="Couldn't establish a connection to AWS")

    bucket_name = get_bucket_name()
    if not bucket_name:
        raise ServiceException(message="Couldn't get bucket name")

    response = await s3_client.get_object(Bucket=bucket_name, Key=file_name)

    response_in_bytes = await response['Body'].read()

    return response_in_bytes


async def upload(file, bucket_name=None, prefix="",
                 file_name=None, content_type=None):
    logger.info("Entering upload()")
    if bucket_name is None:
        bucket_name = get_bucket_name()
    s3_client = await get_s3_client()
    async with s3_client as s3_client:
        if s3_client is None:
            raise ServiceException(
                message="Couldn't establish a connection to AWS")

        await s3_client.upload_fileobj(
            file, bucket_name, (prefix + (file_name if file_name is not None
                                          else file.name)),
            ExtraArgs={'ContentType':
                           (content_type if content_type is not None
                            else file.content_type)})
    logger.info("Exiting upload()")


async def delete(file_name):
    logger.info("Entering delete()")
    bucket_name = get_bucket_name()

    if not bucket_name:
        raise ServiceException(message="Couldn't get bucket name")

    s3_client = await get_s3_client()
    async with s3_client as s3_client:
        if s3_client is None:
            raise ServiceException(
                message="Couldn't establish a connection to AWS")

        response = await s3_client.delete_object(Bucket=bucket_name, Key=file_name)
    logger.info("Exiting delete()")
    return response


async def check_file_existence(file_key):
    logger.info("Entering check_file_existence()")
    bucket_name = get_bucket_name()
    if not bucket_name:
        raise ServiceException(message="Couldn't get bucket name")

    s3_client = await get_s3_client()
    async with s3_client as s3_client:
        if s3_client is None:
            raise ServiceException(message="Couldn't establish a connection to AWS")

        # noinspection PyBroadException
        try:
            await s3_client.head_object(Bucket=bucket_name, Key=file_key)
            exists = True
        except Exception:
            log_error()
            exists = False
    logger.info("Exiting check_file_existence()")
    return exists


async def pre_signed_url(file_key,method:str=None):
    logger.info("Entering pre_signed_url()")
    bucket_name = get_bucket_name()
    if not bucket_name:
        raise ServiceException(message="Couldn't get bucket name")

    s3_client = await get_s3_client()
    async with s3_client as s3_client:
        if s3_client is None:
            raise ServiceException(message="Couldn't establish a connection to AWS")

        if not method:
            method = "get"

        url = await s3_client.generate_presigned_url(
            (method.lower()+'_object'),Params={'Bucket': bucket_name, 'Key': file_key})
    logger.info("Exiting pre_signed_url()")
    return url
