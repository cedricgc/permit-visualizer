# -*- coding: utf-8 -*-
"""Routing and request handler for REST API

The flask app object provides the route decorator to dispatch requests
to the function as described in the decorator argument as well as controlling
the valid HTTP verbs that can be requested to that endpoint. The decorated
handler expects a flask.Response object as the return value.

See http://flask.pocoo.org/docs/latest/quickstart/#about-responses for how
flask converts return values to Response objects.
"""


import uuid

import flask
import flask_pymongo
import structlog


api_bp = flask.Blueprint('api', __name__, url_prefix='/api/v1')
"""Flask.Blueprint: Web API

Initilize API as flask.Blueprint to keep it a modular part of the application
"""

mongo = flask_pymongo.PyMongo()
"""Flask-PyMongo: Database connection

PyMongo has builtin connection pooling and reconnect on failure.
Flask-PyMongo integrates database config with Flask config while also
providing helper functions
"""


@api_bp.route('/hello/', methods=['GET'])
def hello():
    log = structlog.get_logger().bind(request_id=str(uuid.uuid4()))

    log.info('Request at hello route', hello='world')

    return flask.jsonify({'hello': 'world'}), 200
