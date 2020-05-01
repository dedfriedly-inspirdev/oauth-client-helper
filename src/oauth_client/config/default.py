import os
import random

# OAuth2 Settings
OAUTH = {
    'REDIRECT_URL': 'https://localhost:8080/auth_callback',
    'TOKEN_CACHE': os.path.join(os.path.expanduser("~"), ".oauth_token_cache.json"),
    'TOKEN_KEY_PREPEND': 'oauth_client:',
}


# Assuming this write to a redis message queue, setup to use default docker-compose redis host
MESSAGE_QUEUE = {
    'URL': 'redis://redis:6379/0',
}

SESSION_TYPE = 'redis'
SESSION_REDIS = MESSAGE_QUEUE['URL']
SECRET_KEY = ''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])