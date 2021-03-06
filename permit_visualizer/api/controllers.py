# -*- coding: utf-8 -*-
"""Routing and request handler for REST API

The flask app object provides the route decorator to dispatch requests
to the function as described in the decorator argument as well as controlling
the valid HTTP verbs that can be requested to that endpoint. The decorated
handler expects a flask.Response object as the return value.

See http://flask.pocoo.org/docs/latest/quickstart/#about-responses for how
flask converts return values to Response objects.
"""


import datetime
import uuid

import flask
import structlog

import permit_visualizer.api.models as models


api_bp = flask.Blueprint('api', __name__, url_prefix='/api/v1')
"""Flask.Blueprint: Web API

Initilize API as flask.Blueprint to keep it a modular part of the application
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

    try:
        permits, cursor = models.all_permits(limit, after)
    except ValueError:
        log.error('Parameter was not a valid pagination cursor', exc_info=True)
        bad_request = {
            'errors': {
                'after': ['Query parameter was not a valid pagination cursor']
            }
        }

        return flask.jsonify(bad_request), 422

    response = {
        'count': len(permits),
        'cursor': cursor,
        'data': permits,
    }

    return flask.jsonify(response), 200


@api_bp.route('/heatmap/', methods=['GET'])
def heatmap():
    log = structlog.get_logger().bind(request_id=str(uuid.uuid4()))

    # How many items to return, a value over the maximum is set
    # to the maximum value
    limit = flask.request.args.get('limit', 500, type=int)
    if limit > 500:
        limit = 500

    # Cursor to query items afterwards
    after = flask.request.args.get('after', None, type=str)

    # Date parameters that bounds the query
    start = flask.request.args.get('start', None, type=str)
    end = flask.request.args.get('end', None, type=str)

    # Permit types to filter by
    permit_types = flask.request.args.getlist('type', type=str) or None

    # Work classes to filter by
    work_classes = flask.request.args.getlist('class', type=str) or None

    log.debug('query parameters',
              limit=limit,
              after=after,
              start=start,
              end=end,
              permit_types=permit_types,
              work_classes=work_classes)

    try:
        start = datetime.datetime.strptime(start, '%Y-%m-%d')
        end = datetime.datetime.strptime(end, '%Y-%m-%d')
    except TypeError:
        log.error('start and end query params are required', exc_info=True)
        bad_request = {
            'errors': {
                'start': ['Query parameter is required'],
                'end': ['Query parameter is required']
            }
        }

        return flask.jsonify(bad_request), 422
    except ValueError:
        log.error('Parameter was not a valid date', exc_info=True)
        bad_request = {
            'errors': {
                'start': ['Query parameter was not a valid date'],
                'end': ['Query parameter was not a valid date']
            }
        }

        return flask.jsonify(bad_request), 422

    try:
        permits, cursor = models.heatmap_permits(start,
                                                 end,
                                                 limit,
                                                 permit_types=permit_types,
                                                 work_classes=work_classes,
                                                 after=after)
    except ValueError:
        log.error('Parameter was not a valid pagination cursor', exc_info=True)
        bad_request = {
            'errors': {
                'after': ['Query parameter was not a valid pagination cursor']
            }
        }

        return flask.jsonify(bad_request), 422

    response = {
        'count': len(permits),
        'cursor': cursor,
        'data': permits,
    }

    return flask.jsonify(response), 200


@api_bp.route('/count/', methods=['GET'])
def year_count():
    log = structlog.get_logger().bind(request_id=str(uuid.uuid4()))

    # Date parameters that bounds the query
    start = flask.request.args.get('start', None, type=str)
    end = flask.request.args.get('end', None, type=str)

    # Permit types to filter by
    permit_types = flask.request.args.getlist('type', type=str) or None

    # Work classes to filter by
    work_classes = flask.request.args.getlist('class', type=str) or None

    log.debug('query parameters',
              start=start,
              end=end,
              permit_types=permit_types,
              work_classes=work_classes)

    try:
        start = datetime.datetime.strptime(start, '%Y-%m-%d')
        end = datetime.datetime.strptime(end, '%Y-%m-%d')
    except TypeError:
        log.error('start and end query params are required', exc_info=True)
        bad_request = {
            'errors': {
                'start': ['Query parameter is required'],
                'end': ['Query parameter is required']
            }
        }

        return flask.jsonify(bad_request), 422
    except ValueError:
        log.error('Parameter was not a valid date', exc_info=True)
        bad_request = {
            'errors': {
                'start': ['Query parameter was not a valid date'],
                'end': ['Query parameter was not a valid date']
            }
        }

        return flask.jsonify(bad_request), 422

    data = models.annual_count_by_type(start,
                                       end,
                                       permit_types=permit_types,
                                       work_classes=work_classes)

    log.debug('Data for year aggregation', data=data)

    response = {
        'count': len(data),
        'data': data,
    }

    return flask.jsonify(response), 200
