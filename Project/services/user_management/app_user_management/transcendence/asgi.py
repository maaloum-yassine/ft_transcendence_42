# """
# ASGI config for transcendence project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
# """

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transcendence.settings')
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transcendence.settings')

# application = get_asgi_application()



# import os

# from channels.auth import AuthMiddlewareStack
# from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
# from django.core.asgi import get_asgi_application
# from TicTacToe.consumers import TicTacToeConsumer


# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "transcendence.settings")
# # Initialize Django ASGI application early to ensure the AppRegistry
# # is populated before importing code that may import ORM models.
# django_asgi_app = get_asgi_application()

# import chat.routing
# import a_game.routing
# from a_game.middleware import JWTAuthMiddleware

# application = ProtocolTypeRouter(
#     {
#         "http": django_asgi_app,
#         "websocket": AllowedHostsOriginValidator(
#             JWTAuthMiddleware(URLRouter(chat.routing.websocket_urlpatterns + a_game.routing.websocket_urlpatterns) + [path("ws/tictactoe/<str:room_name>/", TicTacToeConsumer.as_asgi())])
#         ),
#     },
#     {
#         "http": get_asgi_application(),
#         "websocket": AuthMiddlewareStack(
#             URLRouter([
#                 path("ws/tictactoe/<str:room_name>/", TicTacToeConsumer.as_asgi()),
#             ])
#         ),
#     }
# )

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path  # <-- Importation de 'path' manquante
from TicTacToe.consumers import TicTacToeConsumer  # Assure-toi d'importer TicTacToeConsumer
# Import des routes
import chat.routing
import a_game.routing
import TicTacToe.routing
from a_game.middleware import JWTAuthMiddleware
import tournament.routing

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
                    chat.routing.websocket_urlpatterns + a_game.routing.websocket_urlpatterns + tournament.routing.websocket_urlpatterns + [
                        # Ajout de la route pour TicTacToe
                        path("ws/tictactoe/<str:room_name>/", TicTacToeConsumer.as_asgi())
                    ]
                )
            )
        ),
    }
)
