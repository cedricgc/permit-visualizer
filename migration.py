# -*- coding: utf-8 -*-


import logging
import os
import sys

import pymongo
import structlog


def setup_logging():
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


def main():
    log = structlog.get_logger()

    database_url = os.environ['DATABASE_URL']

    log.info('Connecting to database')

    mongo_client = pymongo.MongoClient(database_url)

    log.info('Creating indexes')

    db = mongo_client['permits']
    index = db['all_permits']
    index.create_index([('project_id', pymongo.ASCENDING)], unique=True)

    log.info('Indexes on all_permits collection',
             indexes=index.index_information())
    log.info('Creating views based on all_permits')

    try:
        pipeline = geographic_pipeline()
        geographic = db.create_collection('geographic',
                                          viewOn='all_permits',
                                          pipeline=pipeline)
    except pymongo.errors.CollectionInvalid:
        log.warning('Collection already exists')

    log.info('Created collections and views', all=db.collection_names())

    return 0


def geographic_pipeline():
    pipeline = [
        {
            '$project': {
                'location': True,
                'latitude': True,
                'longitude': True,
            }
        },
    ]

    return pipeline


if __name__ == '__main__':
    setup_logging()
    return_code = main()
    sys.exit(return_code)
