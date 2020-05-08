#!/usr/bin/env python
import pkg_resources
import os
import json
import logging
from flask import Flask
from flask_talisman import Talisman
from flask_bootstrap import Bootstrap
# from flask_session import Session
from oauth_client.config import settings

pkg_resources.declare_namespace(__name__)


# Global libraries
bootstrap = Bootstrap()

csp = {
 'default-src': [
        '\'self\'',
        'cdnjs.cloudflare.com',
        'maxcdn.bootstrapcdn.com',
        '\'sha256-ht06exDupLia1P7H1fk43dAnjeDqDnwxr8bp12ydka8=\'',
        '\'sha256-duWm3IZ3ZF3249nh6dr98szvNyiz/bfe0sWsB+uI53E=\'',
    ]
}
talisman = Talisman()


def create_app():
    """ Initialize our application """
    from oauth_client.config import settings
    app = Flask(__name__, instance_relative_config=False)

    app.config.update(**settings.FLASK)

    bootstrap.init_app(app)
    talisman.init_app(app, content_security_policy=csp)

    with app.app_context():
        from oauth_client import routes

        return app