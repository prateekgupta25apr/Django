import email
import json

import boto3
from django.conf import settings
from django.http import HttpResponse

from main.LogManager import logger
from util import get_success_response
from util.exceptions import log_error, SampleProjectException


def get_s3_client():
    session = boto3.Session()
    # Fetching from AWS CLI
    s3_client = session.client('s3')

    creds = session.get_credentials()
    print(creds.access_key, " : ", creds.secret_key)

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
        result = dict()
        result['message'] = "Success"
        return get_success_response(result)
    except SampleProjectException as e:
        return e.get_error_response()
    except Exception as e:
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


def get_email_content(request):
    message_id = request.GET.get('message_id')

    # Fetch the email file from S3
    file_key = f"emails/{message_id}"
    email_file = get_s3_client().get_object(Bucket="pg25", Key=file_key)
    email_content = email_file['Body'].read().decode('utf-8')

    # Parse the email content
    msg = email.message_from_string(email_content)

    email_details = {
        'sender': msg['From'],
        'subject': msg['Subject'],
        'body': None
    }

    if msg.is_multipart():
        for part in msg.get_payload():
            content_type = part.get_content_type()
            if content_type == 'text/plain':
                # Decode and store plain text body
                charset = part.get_content_charset() or 'utf-8'
                email_details['body'] = part.get_payload(decode=True).decode(charset).strip()
                break  # Stop processing after finding plain text body
    else:
        # Single part email, directly decode the body
        email_details['body'] = msg.get_payload(decode=True).strip()

    return HttpResponse(json.dumps(email_details), content_type="application/json")


def get_file(request):
    # Fetch the file from S3
    file_key = request.GET.get('file_name')
    email_file = get_s3_client().get_object(Bucket="pg25", Key=file_key)
    file_content = email_file['Body'].read()

    response = HttpResponse(file_content, content_type="application/octet-stream")
    response['Content-Disposition'] = f'attachment; filename="{file_key}"'
    return response
