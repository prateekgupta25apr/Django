import boto3
from django.conf import settings
from django.http import HttpResponse

from util import get_success_response
from util.exceptions import log_error, PracticeException


def upload_file(request):
    # noinspection PyBroadException
    try:
        file=request.FILES['file']
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        s3_client.upload_fileobj(
            file,
            settings.AWS_STORAGE_BUCKET_NAME,
            file.name,
            ExtraArgs={'ContentType': file.content_type}
        )
        result=dict()
        result['message']="Success"
        return get_success_response(result)
    except PracticeException as e:
        return e.get_error_response()
    except Exception:
        log_error()
        return PracticeException().get_error_response()

