import os
from dynaconf import LazySettings

settings = LazySettings(
    DEBUG_LEVEL_FOR_DYNACONF=os.getenv('OAUTHCLIENT_DEBUG_LEVEL', 'DEBUG'),
    ENV_FOR_DYNACONF=os.getenv('OAUTHCLIENT_ENV', 'development'),
    ENVVAR_PREFIX_FOR_DYNACONF='OAUTHCLIENT')

settings.set('ROOT_DIR', os.path.dirname(os.path.abspath(os.path.join(os.path.abspath(__file__), "../"))))

settings.load_file(os.path.join(settings.ROOT_DIR,'config/default.py'), env='default')
settings.load_file(os.path.join(settings.ROOT_DIR,'settings.py'))