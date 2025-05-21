import email
import json

from django.http import HttpResponse, FileResponse

from prateek_gupta.LogManager import logger
from prateek_gupta.aws_sync import (check_file_existence, get_file_content_in_bytes,
                                    get_bucket_name, upload, delete, \
                                    get_s3_client, pre_signed_url)
from prateek_gupta.exceptions import ServiceException
from prateek_gupta.utils import (request_mapping, async_iterator)
from utils import (get_success_response, get_api_response, get_error_response)


@request_mapping("GET")
def get_file(request):
    # noinspection PyBroadException
    try:
        file_key = request.GET.get('file_name')
        if check_file_existence(file_key):
            file_content = get_file_content_in_bytes(file_key)
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
def upload_file(request):
    logger.info("Entering upload_file()")
    # noinspection PyBroadException
    try:
        file = request.FILES['file']

        upload(file)
        response = dict()
        response['message'] = "Successfully uploaded the file : " + file.name
        response = get_success_response(response)
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing upload_file()")
    return response


@request_mapping("DELETE")
def delete_file(request):
    logger.info("Entering delete_file()")
    # noinspection PyBroadException
    try:
        file_name = request.GET['file_name']

        delete(file_name)
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
def get_pre_signed_url(request):
    # noinspection PyBroadException
    try:
        # Fetch the file from S3
        file_key = request.GET.get('file_name')

        url = pre_signed_url(file_key)
        response = get_success_response({"message": "Generated pre-signed url successfully",
                                         "Pre-Signed URL": url})

    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    return response


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
