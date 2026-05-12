import json
from email.mime.image import MIMEImage

import requests
from asgiref.sync import sync_to_async
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.db import connections, transaction
import mysql.connector
import django


def get_api_response(body, status):
    """Method to return generic JSON response for an API"""
    try:
        if type(body) in [dict, list]:
            response = json.dumps(body)
        else:
            response = body
        return HttpResponse(response, content_type="application/json", status=status)
    except Exception as e:
        print(str(e))


def get_success_response(body):
    """Method to return generic JSON response for an API"""
    return get_api_response(body, 200)


def get_error_response(exception, request=None):
    """Method to return response for errors"""
    from prateek_gupta.LogManager import logger
    from prateek_gupta.exceptions import log_error, ServiceException
    if isinstance(exception, ServiceException):
        message = exception.message
        status_id = exception.status_id
    else:
        message = str(exception)
        status_id = None

    # Logging error
    log_error()

    if request is not None:
        logger.error("Error while responding the api : " + request.path)

    response = dict()
    if status_id is not None:
        response["message"] = message
        return get_api_response(response, status_id)
    else:
        response["message"] = message
        return get_api_response(response,
                                ServiceException.ExceptionType.UNKNOWN_ERROR.value)


@sync_to_async
def execute_query(query, method=None, thread_execution=None):
    # noinspection PyBroadException
    try:
        if not thread_execution:
            try:
                connection = connections['default']

                with transaction.atomic():
                    with connection.cursor() as cursor:
                        result = cursor.execute(query)

                        if method == 'fetchone':
                            result = cursor.fetchone()
                        elif method == 'fetchall':
                            result = cursor.fetchall()

                return result
            except django.db.utils.OperationalError:
                from prateek_gupta import exceptions
                exceptions.log_error()
                from prateek_gupta.LogManager import logger
                logger.info(f"DB_EXECUTION_ERROR: Executing query with new connection")
                return execute_thread_query(query, method)
        else:
            return execute_thread_query(query, method)
    except Exception as e:
        from prateek_gupta import exceptions
        exceptions.log_error()
        raise e


def execute_thread_query(query, method=None):
    try:
        from prateek_gupta import exceptions, configuration_properties
        with (mysql.connector.connect(
                host=configuration_properties['db_host'],
                user=configuration_properties['db_user_name'],
                password=configuration_properties['db_password']) as manual_connection):
            with manual_connection.cursor() as manual_cursor:
                manual_cursor.execute(query)

                if method == 'fetchone':
                    result = manual_cursor.fetchone()
                elif method == 'fetchall':
                    result = manual_cursor.fetchall()
                else:
                    result = manual_cursor.rowcount
                    manual_connection.commit()

                return result

    except mysql.connector.Error as e:
        from prateek_gupta import exceptions
        exceptions.log_error()
        from prateek_gupta.LogManager import logger
        logger.info(f"DB_EXECUTION_ERROR: Even manual connection failed")
        raise e


def validate_user_login(request):
    from prateek_gupta.exceptions import ServiceException
    if request.user_context.user_id <= 0:
        raise ServiceException(exception_type=ServiceException.ExceptionType.LOGIN_REQUIRED)


def send_email_sync(
        from_email: str, to_emails: str, subject: str, content: str,
        attachments: str = None):
    failed_attachments = []
    from prateek_gupta.emails_sync import (
        get_plain_content, get_html_content_and_inline_attachments,
        get_file_content_in_bytes)
    from prateek_gupta.utils import get_content_type
    email = EmailMultiAlternatives(
        subject=subject,
        body=get_plain_content(content),
        from_email=from_email,
        to=to_emails.split(","),
    )

    html_content, inline_attachment = get_html_content_and_inline_attachments(content)
    email.attach_alternative(html_content, "text/html")

    # Adding inline attachments
    for attachment in inline_attachment:
        # noinspection PyBroadException
        try:
            if "https://" not in attachment.get("file_url", ""):
                file_content = get_file_content_in_bytes(attachment["file_url"])
            else:
                response = requests.get(attachment["file_url"])
                if response.status_code == 200:
                    file_content = response.content
                else:
                    file_content = None
        except Exception:
            file_content = None

        if file_content:
            mime_image = MIMEImage(file_content)
            mime_image.add_header("Content-ID", attachment["cid"])
            mime_image.add_header(
                "Content-Disposition", "inline",
                filename=attachment["file_key"]
            )
            email.attach(mime_image)
        else:
            failed_attachments.append(attachment["file_key"])

    # Adding normal attachment if there
    if attachments:
        attachments = json.loads(attachments)
        for attachment in attachments:
            # noinspection PyBroadException
            try:
                if attachment.get("file_key", ""):
                    file_content = get_file_content_in_bytes(attachment["file_key"])
                else:
                    response = requests.get(attachment["file_url"])
                    if response.status_code == 200:
                        file_content = response.content
                    else:
                        file_content = None
            except Exception:
                file_content = None

            if file_content:
                content_type_details = get_content_type(attachment["file_name"])
                email.attach(
                    filename=attachment["file_name"],
                    content=file_content,
                    mimetype=f"{content_type_details['maintype']}/"
                             f"{content_type_details['subtype']}",
                )
            else:
                failed_attachments.append(attachment["file_name"])
    email.send()
    return failed_attachments


async def send_email_async(
        from_email: str, to_emails: str, subject: str, content: str,
        attachments: str = None):
    failed_attachments = []
    from prateek_gupta.emails_async import (
        get_plain_content, get_html_content_and_inline_attachments,
        get_file_content_in_bytes)
    from prateek_gupta.utils import get_content_type
    from prateek_gupta.utils import execute_as_async
    email = EmailMultiAlternatives(
        subject=subject,
        body=get_plain_content(content),
        from_email=from_email,
        to=to_emails.split(","),
    )

    html_content, inline_attachment = get_html_content_and_inline_attachments(content)
    email.attach_alternative(html_content, "text/html")

    # Adding inline attachments
    for attachment in inline_attachment:
        # noinspection PyBroadException
        try:
            if "https://" not in attachment.get("file_url", ""):
                file_content = await get_file_content_in_bytes(attachment["file_url"])
            else:
                response = await execute_as_async(requests.get, attachment["file_url"])
                if response.status_code == 200:
                    file_content = response.content
                else:
                    file_content = None
        except Exception:
            file_content = None

        if file_content:
            mime_image = MIMEImage(file_content)
            mime_image.add_header("Content-ID", attachment["cid"])
            mime_image.add_header(
                "Content-Disposition", "inline", filename=attachment["file_key"]
            )
            email.attach(mime_image)
        else:
            failed_attachments.append(attachment["file_key"])

    # Adding normal attachment if there
    if attachments:
        attachments = json.loads(attachments)
        for attachment in attachments:
            # noinspection PyBroadException
            try:
                if attachment.get("file_key", ""):
                    file_content = await get_file_content_in_bytes(attachment["file_key"])
                else:
                    response = await execute_as_async(requests.get, attachment["file_url"])
                    if response.status_code == 200:
                        file_content = response.content
                    else:
                        file_content = None
            except Exception:
                file_content = None

            if file_content:
                content_type_details = get_content_type(attachment["file_name"])
                email.attach(
                    filename=attachment["file_name"],
                    content=file_content,
                    mimetype=f"{content_type_details['maintype']}/"
                             f"{content_type_details['subtype']}",
                )
            else:
                failed_attachments.append(attachment["file_name"])
    email.send()
    return failed_attachments
