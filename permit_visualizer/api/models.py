# -*- coding: utf-8 -*-


import bson
import flask_pymongo


mongo = flask_pymongo.PyMongo()
"""Flask-PyMongo: Database connection

PyMongo has builtin connection pooling and reconnect on failure.
Flask-PyMongo integrates database config with Flask config while also
providing helper functions
"""


def all_permits(limit, after=None):
    if after and bson.objectid.ObjectId.is_valid(after):
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
