import os
import random

# OAuth2 Settings
OAUTH = {
    'REDIRECT_URL': 'https://127.0.0.1:8080/auth_callback',
    'TOKEN_CACHE': os.path.join(os.path.expanduser("~"), ".oauth_token_cache.json"),
    'TOKEN_KEY_PREPEND': 'oauth_client:',
}


# Assuming this write to a redis message queue, setup to use default docker-compose redis host
MESSAGE_QUEUE = {
    'URL': 'redis://redis:6379/0',
}

FLASK = {
    # https://flask.palletsprojects.com/en/1.1.x/config/
    'APP': 'oauth-client-helper',
    'ENV': 'development',
    'DEBUG': True,
    'SECRET_KEY': ''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
}