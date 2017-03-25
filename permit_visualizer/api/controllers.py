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

import bson
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


@api_bp.route('/permits/', methods=['GET'])
def index_permits():
    log = structlog.get_logger().bind(request_id=str(uuid.uuid4()))

    # How many items to return, a value over the maximum is set
    # to the maximum value
    limit = flask.request.args.get('limit', 25, type=int)
    if limit > 50:
        limit = 50
    # Cursor to query items afterwards
    after = flask.request.args.get('after', None, type=str)

    log.debug('query parameters', limit=limit, after=after)

    query = {
        '_id': {
            '$gt': bson.objectid.ObjectId(after),
        },
    }
    if after:
        cursor = mongo.db['all_permits'].find(query).limit(limit)
    else:
        cursor = mongo.db['all_permits'].find().limit(limit)

    permits = [permit for permit in cursor]
    count = len(permits)
    if count > 0:
        query_cursor = str(permits[-1]['_id'])
    else:
        query_cursor = None

    for permit in permits:
        del permit['_id']

    response = {
        'count': len(permits),
        'cursor': query_cursor,
        'data': permits,
    }

    return flask.jsonify(response), 200
