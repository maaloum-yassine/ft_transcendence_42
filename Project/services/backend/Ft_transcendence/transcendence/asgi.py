
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path  # <-- Importation de 'path' manquante
from TicTacToe.consumers import TicTacToeConsumer  # Assure-toi d'importer TicTacToeConsumer
from channels.security.websocket import AllowedHostsOriginValidator
# Import des routes
import chat.routing
import a_game.routing
import TicTacToe.routing
from a_game.middleware import JWTAuthMiddleware

# Assurez-vous que Django est configuré avant de démarrer
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "transcendence.settings")

# Initialisation de l'application ASGI Django
django_asgi_app = get_asgi_application()

# Définition de l'application ASGI
application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,  # Application HTTP standard
        "websocket": AllowedHostsOriginValidator(
            JWTAuthMiddleware(
                URLRouter(
                    chat.routing.websocket_urlpatterns + a_game.routing.websocket_urlpatterns + [
                        path("ws/tictactoe/<str:room_name>/", TicTacToeConsumer.as_asgi())
                    ]
                )
            )
        ),
    }
)
