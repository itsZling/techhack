"""
ASGI config for techhack project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import home.routing # Import your app's routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_project.settings')

application = ProtocolTypeRouter({
    # Handle standard HTTP requests
    "http": get_asgi_application(),
    
    # Handle WebSocket connections
    "websocket": AuthMiddlewareStack(
        URLRouter(
            game_app.routing.websocket_urlpatterns + lobby.routing.websocket_urlpatterns
        )
    ),
})