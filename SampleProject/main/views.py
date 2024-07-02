from django.conf import settings
from django.http import HttpResponse


def test(request):
    return HttpResponse("Success")
