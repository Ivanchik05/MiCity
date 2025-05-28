import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mycity.settings')
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import places.routing  # теперь можно импортировать, т.к. настройки инициализированы

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            places.routing.websocket_urlpatterns
        )
    ),
})
