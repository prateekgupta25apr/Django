from django.http import HttpResponse
import json
from django.core.mail import send_mail


def send_email(request):
    data = json.loads(request.body)
    # Sending email to the user # (Notes [6])
    sender_email=data["name"]+"<"+data["emailFrom"]+">"
    recipients_emails = list()
    for i in data["emailTo"].split(","):
        recipients_emails.append(i)
    send_mail(data["emailSubject"], data["emailBody"], sender_email, recipients_emails)
    return HttpResponse("Success", content_type="text/plain")
