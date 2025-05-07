"""
ASGI config for SampleProject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from prateek_gupta import on_load

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SampleProject.settings')


class ASGiApplication:

    def __init__(self):
        self.app = get_asgi_application()


    async def __call__(self, scope, receive, send):
        # if scope['type'] == 'lifespan':
        #     await on_load()
        await self.app(scope, receive, send)


application = ASGiApplication()
