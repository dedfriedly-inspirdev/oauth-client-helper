#!/usr/bin/env python
import pkg_resources
import os
from dynaconf import LazySettings

pkg_resources.declare_namespace(__name__)


settings = LazySettings(
    DEBUG_LEVEL_FOR_DYNACONF=os.getenv('OAUTHCLIENT_DEBUG_LEVEL', 'WARNING'),
    ENV_FOR_DYNACONF=os.getenv('OAUTHCLIENT_ENV', 'development'),
    ENVVAR_PREFIX_FOR_DYNACONF='OAUTHCLIENT')

settings.set('ROOT_DIR', os.path.dirname(os.path.abspath(__file__)))

settings.load_file(os.path.join(settings.ROOT_DIR,'config/default.py'), env='default')
settings.load_file(os.path.join(settings.ROOT_DIR,'settings.py'))