import datetime
import email
import json
import os
import smtplib
from email.message import EmailMessage
from io import BytesIO

import requests
from bs4 import BeautifulSoup

from prateek_gupta import configuration_properties
from prateek_gupta.aws_sync import (
    get_bucket_name, get_s3_client, upload, pre_signed_url, extract_file_name,
    update_file_name, get_file_content_in_bytes
)
from prateek_gupta.exceptions import ServiceException
from prateek_gupta.utils import get_content_type


def get(message_id=None, file_path=None, fetch_file_url=False):
    bucket_name = get_bucket_name()
    if not bucket_name:
        raise ServiceException(message="Couldn't get bucket name")

    email_content = None
    if message_id:
        # Fetch the email file from S3
        file_key = f"emails/{message_id}"
        email_file = get_s3_client().get_object(Bucket=bucket_name, Key=file_key)
        email_content = email_file['Body'].read().decode('utf-8')

    if file_path:
        file_details = open(file_path, "r")
        email_content = file_details.read()

    if not email_content:
        raise ServiceException(message="Couldn't get email content")

    # Parse the email content
    msg = email.message_from_string(email_content, policy=email.policy.default)

    email_details = {
        'sender': msg['From'],
        'subject': msg['Subject']
    }

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = part.get_content_disposition()

            if content_type == "text/html" and disposition is None:
                email_details["html_body"] = part.get_content()

            elif content_type == "text/plain" and disposition is None:
                email_details['text_body'] = part.get_content()
    else:
        email_details["text_body"] = msg.get_content()

    attachments = []

    for part in msg.iter_attachments():
        attachment = {
            "filename": part.get_filename(),
            "mime_type": part.get_content_type(),
        }
        if part.get_content_disposition() == "inline":
            attachment["content-type"] = "Inline"
            attachment["content_id"] = part["Content-ID"]
        else:
            attachment["content-type"] = "Attachment"

        if fetch_file_url:
            file_name, file_ext = os.path.splitext(part.get_filename())
            attachment_name = (
                f"emails_attachment/"
                f"{file_name}_{datetime.datetime.now().timestamp()}{file_ext}")
            upload(BytesIO(
                part.get_content()), file_key=attachment_name,
                content_type=part.get_content_type())
            attachment["file_url"] = pre_signed_url(attachment_name)
        attachments.append(attachment)

    email_details["attachments"] = attachments

    return email_details


def send(from_email: str, to_email: str, subject: str,
         content: str, attachments: str = None):
    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    alt = EmailMessage()
    alt.set_content(get_plain_content(content))

    html_content, inline_attachment = get_html_content_and_inline_attachments(content)
    alt.add_alternative(html_content, subtype="html")

    # Starting multipart/related
    msg.make_related()

    # Adding text content
    msg.attach(alt)

    # Adding inline attachments
    for attachment in inline_attachment:
        if "https://" not in attachment.get("file_url", ""):
            file_content = get_file_content_in_bytes(attachment["file_url"])
        else:
            response = requests.get(attachment["file_url"])
            if response.status_code == 200:
                file_content = response.content
            else:
                file_content = None

        if file_content:
            content_type_details = get_content_type(attachment["file_key"])
            msg.add_related(
                file_content,
                maintype=content_type_details["maintype"],
                subtype=content_type_details["subtype"],
                cid=attachment["cid"],
                filename=attachment["file_key"]
            )

    # Adding normal attachment if there
    if attachments:
        attachments = json.loads(attachments)
        for attachment in attachments:
            if attachment.get("file_key", ""):
                file_content = get_file_content_in_bytes(attachment["file_key"])
            else:
                response = requests.get(attachment["file_url"])
                if response.status_code == 200:
                    file_content = response.content
                else:
                    file_content = None

            if file_content:
                content_type_details = get_content_type(attachment["file_name"])
                msg.add_attachment(
                    file_content,
                    maintype=content_type_details["maintype"],
                    subtype=content_type_details["subtype"],
                    filename=attachment["file_name"]
                )

    if configuration_properties.get("EMAILS_SEND_GRID_ENABLED", ""):
        server = configuration_properties.get("EMAILS_SEND_GRID_SERVER")
        port = int(configuration_properties.get("EMAILS_SEND_GRID_PORT"))
        username = configuration_properties.get("EMAILS_SEND_GRID_USERNAME")
        password = configuration_properties.get("EMAILS_SEND_GRID_PASSWORD")
    else:
        server = configuration_properties.get("EMAILS_SMTP_SERVER")
        port = int(configuration_properties.get("EMAILS_SMTP_PORT"))
        username = configuration_properties.get("EMAILS_SMTP_USERNAME")
        password = configuration_properties.get("EMAILS_SMTP_PASSWORD")
    # Send email
    with smtplib.SMTP(server, port) as server:
        server.ehlo()
        server.starttls()
        server.login(username, password)
        server.send_message(msg)


def get_plain_content(html_content: str):
    parser = BeautifulSoup(html_content, "html.parser")
    tags = parser.find_all("img")

    for tag in tags:
        p_tag = parser.new_tag("p")
        alt_message = tag.attrs.get("alt", "")
        alt_message = alt_message if alt_message else "image"
        p_tag.string = f"[{alt_message}]"
        tag.replace_with(p_tag)

    return parser.text


def get_html_content_and_inline_attachments(html_content: str):
    parser = BeautifulSoup(html_content, "html.parser")
    tags = parser.find_all("img")
    inline_attachments = []

    for tag in tags:
        img_url = tag.attrs.get("src", "")
        file_name = extract_file_name(img_url, only_file_name=True)
        file_key = update_file_name(file_name)
        cid, ext = os.path.splitext(file_key)
        tag.attrs["src"] = f"cid:{cid}"
        inline_attachments.append({
            "file_key": file_key, "file_url": img_url, "cid": cid, "ext": ext})
    return str(parser), inline_attachments


def process_email(
        message_id=None, file_path=None, to_email: str = None):
    bucket_name = get_bucket_name()
    if not bucket_name:
        raise ServiceException(message="Couldn't get bucket name")

    email_content = None
    if message_id:
        # Fetch the email file from S3
        file_key = f"emails/{message_id}"
        email_file = get_s3_client().get_object(Bucket=bucket_name, Key=file_key)
        email_content = email_file['Body'].read().decode('utf-8')

    if file_path:
        file_details = open(file_path, "r")
        email_content = file_details.read()

    if not email_content:
        raise ServiceException(message="Couldn't get email content")

    # Parse the email content
    original = email.message_from_string(email_content, policy=email.policy.default)
    from_email = "prateek.gupta25apr@gmail.com"
    if not to_email:
        to_email = "prateek.gupta25apr@gmail.com"
    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = "Email Received"

    text_body = (f"Received an email from {original.get('From', '')} "
                 f"with subject {original.get('Subject', '')}")
    html_body = (f"<p>Received an email from <b>{original.get('From', '')}</b> "
                 f"with subject <b>{original.get('Subject', '')}</b></p>")

    if original.is_multipart():
        for part in original.walk():
            content_type = part.get_content_type()
            disposition = part.get_content_disposition()

            if disposition is None:
                if content_type == "text/plain":
                    text_body += part.get_content()
                elif content_type == "text/html":
                    html_body += part.get_content()
    else:
        text_body += original.get_content()

    # Set body correctly
    if html_body:
        msg.set_content(text_body or " ")
        msg.add_alternative(html_body, subtype="html")
    else:
        msg.set_content(text_body or "")

    for part in original.iter_attachments():
        if part.get_content_disposition() == "inline":
            msg.add_attachment(
                part.get_content(),
                maintype=part.get_content_maintype(),
                subtype=part.get_content_subtype(),
                cid=part["Content-ID"],
                filename=part.get_filename()
            )
        else:
            msg.add_attachment(
                part.get_content(),
                maintype=part.get_content_maintype(),
                subtype=part.get_content_subtype(),
                filename=part.get_filename()
            )

    if configuration_properties.get("EMAILS_SEND_GRID_ENABLED", ""):
        server = configuration_properties.get("EMAILS_SEND_GRID_SERVER")
        port = int(configuration_properties.get("EMAILS_SEND_GRID_PORT"))
        username = configuration_properties.get("EMAILS_SEND_GRID_USERNAME")
        password = configuration_properties.get("EMAILS_SEND_GRID_PASSWORD")
    else:
        server = configuration_properties.get("EMAILS_SMTP_SERVER")
        port = int(configuration_properties.get("EMAILS_SMTP_PORT"))
        username = configuration_properties.get("EMAILS_SMTP_USERNAME")
        password = configuration_properties.get("EMAILS_SMTP_PASSWORD")

    # Send email
    with smtplib.SMTP(server, port) as server:
        server.ehlo()
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
