import json

from django.http import HttpResponse


def get_success_response(body):
    """Method to return generic JSON response for an API"""
    if type(body) is dict:
        response = json.dumps(body)
    else:
        response = body
    return HttpResponse(response, content_type="application/json", status=200)