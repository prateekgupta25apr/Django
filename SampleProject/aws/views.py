import boto3
from django.conf import settings
from django.http import HttpResponse

from main.LogManager import logger
from util import get_success_response
from util.exceptions import log_error, SampleProjectException


def get_s3_client():
    # Fetching from AWS CLI
    s3_client = boto3.client('s3')

    if s3_client is None:
        # Preparing client from creds
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
    else:
        logger.error("Got creds from AWS CLI")

    return s3_client


def upload_file(request):
    # noinspection PyBroadException
    try:
        file = request.FILES['file']
        get_s3_client().upload_fileobj(
            file,
            settings.AWS_STORAGE_BUCKET_NAME,
            file.name,
            ExtraArgs={'ContentType': file.content_type}
        )
        result=dict()
        result['message']="Success"
        return get_success_response(result)
    except SampleProjectException as e:
        return e.get_error_response()
    except Exception:
        log_error()
        return SampleProjectException().get_error_response()


def delete_file(request):
    # noinspection PyBroadException
    try:
        file_name = request.POST['file']
        response = get_s3_client().delete_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=file_name
        )
        print(response)
        result = dict()
        result['message'] = "Success"
        return get_success_response(result)
    except SampleProjectException as e:
        return e.get_error_response()
    except Exception:
        log_error()
        return SampleProjectException().get_error_response()

