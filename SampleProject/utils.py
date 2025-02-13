import json

from django.http import HttpResponse


def get_api_response(body,status):
    """Method to return generic JSON response for an API"""
    try:
        if type(body) is dict:
            response = json.dumps(body)
        else:
            response = body
        return HttpResponse(response, content_type="application/json", status=status)
    except Exception as e:
        print(str(e))

def get_success_response(body):
    """Method to return generic JSON response for an API"""
    return get_api_response(body,200)