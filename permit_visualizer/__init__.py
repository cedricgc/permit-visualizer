# -*- coding: utf-8 -*-


import logging
import sys

import flask
import structlog


def create_app():
    """Factory that returns Flask application object

    See http://flask.pocoo.org/docs/latest/patterns/appfactories/ for motivation
    """
    app = flask.Flask(__name__)
    app.config.from_object('config.Config')
    app.static_folder = app.config['STATIC_FILES']
    app.template_folder = app.config['TEMPLATES']

    app.url_map.strict_slashes = False
    """Disables Werkzeug's strict route interpretation

    There are good reasons for enforcing strict slashes for form posts and
    indexability, but it is inconvienent when interacting with an API so
    it is disabled.

    See: http://flask.pocoo.org/docs/latest/quickstart/#variable-rules
    """

    # Initilize flask extensions
    from permit_visualizer.api.models import mongo

    mongo.init_app(app, config_prefix='DATABASE')

    # We import controllers after top level object or interpreter would crash
    # due to circular dependencies
    # Ensure route controllers are executed by interpreter
    from permit_visualizer.api.controllers import api_bp
    from permit_visualizer.frontend.controllers import frontend_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(frontend_bp)

    return app


app = create_app()
"""Flask: project application instance

The Flask object handles the application routing, configuration, and HTTP
Middleware through WSGI.
"""


@app.before_first_request
def setup_logging():
    # Flask logger
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.DEBUG)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    stdout_handler = logging.StreamHandler(sys.stdout)
    root_logger.addHandler(stdout_handler)

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt='iso', utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
