# -*- coding: utf-8 -*-


import logging
import sys

import flask


def create_app():
    """Factory that returns Flask application object

    See http://flask.pocoo.org/docs/latest/patterns/appfactories/ for motivation
    """
    app = flask.Flask(__name__)

    app.url_map.strict_slashes = False
    """Disables Werkzeug's strict route interpretation

    There are good reasons for enforcing strict slashes for form posts and
    indexability, but it is inconvienent when interacting with an API so
    it is disabled.

    See: http://flask.pocoo.org/docs/latest/quickstart/#variable-rules
    """

    # We import controllers after top level object or interpreter would crash
    # due to circular dependencies
    # Ensure route controllers are executed by interpreter
    from permit_visualizer.api.controllers import api_bp

    app.register_blueprint(api_bp)

    return app


app = create_app()
"""Flask: project application instance

The Flask object handles the application routing, configuration, and HTTP
Middleware through WSGI.
"""


@app.before_first_request
def setup_logging():
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.DEBUG)
