# -*- coding: utf-8 -*-


import bson
import flask_pymongo
import structlog


mongo = flask_pymongo.PyMongo()
"""Flask-PyMongo: Database connection

PyMongo has builtin connection pooling and reconnect on failure.
Flask-PyMongo integrates database config with Flask config while also
providing helper functions
"""


def all_permits(limit, after=None):
    if not bson.objectid.ObjectId.is_valid(after) and after is not None:
        raise ValueError(f'{after} is not a valid MongoDB ObjectID')

    if after is not None:
        query = {
            '_id': {
                '$gt': bson.objectid.ObjectId(after),
            },
        }
        cursor = mongo.db['all_permits'].find(query).limit(limit)
    else:
        cursor = mongo.db['all_permits'].find().limit(limit)

    permits = [permit for permit in cursor]
    count = len(permits)
    if count > 0:
        pagination_cursor = str(permits[-1]['_id'])
    else:
        pagination_cursor = None

    for permit in permits:
        del permit['_id']

    return permits, pagination_cursor


def heatmap_permits(start, end, limit, after=None):
    if not bson.objectid.ObjectId.is_valid(after) and after is not None:
        raise ValueError(f'{after} is not a valid MongoDB ObjectID')

    query = {}
    if after is not None:
        query = {
            '_id': {
                '$gt': bson.objectid.ObjectId(after),
            },
            'issue_date': {
                '$gt': start,
                '$lt': end,
            },
        }
    else:
        query = {
            'issue_date': {
                '$gt': start,
                '$lt': end,
            },
        }

    cursor = mongo.db['heatmap'].find(query).limit(limit)

    permits = [permit for permit in cursor]

    count = len(permits)
    if count > 0:
        pagination_cursor = str(permits[-1]['_id'])
    else:
        pagination_cursor = None

    for permit in permits:
        del permit['_id']

    return permits, pagination_cursor
