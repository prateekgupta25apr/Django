from prateek_gupta.emails_async import get, send, process_email
from prateek_gupta.exceptions import module_lock_check, ServiceException
from prateek_gupta.utils import request_mapping
from utils import get_success_response, get_error_response, send_email_async


@request_mapping("GET")
async def get_email_content(request):
    # noinspection PyBroadException
    try:
        module_lock_check("EMAILS_ENABLED", "A")

        message_id = request.GET.get('message_id', None)
        file_path = request.GET.get('file_path', None)
        fetch_file_url = request.GET.get('fetch_file_url', False)

        email_details = await get(
            message_id=message_id, file_path=file_path, fetch_file_url=fetch_file_url)
        response = get_success_response(email_details)
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    return response


@request_mapping("POST")
async def send_email(request):
    # noinspection PyBroadException
    try:
        module_lock_check("EMAILS_ENABLED", "A")

        from_email = request.POST.get('from_email', None)
        to_email = request.POST.get('to_email', None)
        subject = request.POST.get('subject', None)
        content = request.POST.get('content', None)
        attachments = request.POST.get('attachments', None)
        native = request.POST.get('native', False)

        if native:
            await send_email_async(
                from_email=from_email, to_emails=to_email, subject=subject,
                content=content, attachments=attachments)
        else:
            await send(
                from_email=from_email, to_email=to_email, subject=subject,
                content=content, attachments=attachments)
        response = get_success_response({"message": "Successfully sent email"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    return response


@request_mapping("POST")
async def process_email_request(request):
    # noinspection PyBroadException
    try:
        module_lock_check("EMAILS_ENABLED", "A")

        message_id = request.POST.get('message_id', None)
        file_path = request.POST.get('file_path', None)
        to_email = request.POST.get('to_email', None)

        await process_email(
            message_id=message_id, file_path=file_path, to_email=to_email)
        response = get_success_response({"message": "Successfully processed email"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    return response
