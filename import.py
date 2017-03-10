# -*- coding: utf-8 -*-


import logging
import os
import sys

import requests
import sodapy
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

    domain = os.environ.get('DOMAIN')
    app_token = os.environ.get('APP_TOKEN')
    dataset_id = os.environ.get('DATASET_ID')

    client = sodapy.Socrata(domain, app_token)

    log.debug('Fetching permits')

    query = {
        'select': 'project_id,applieddate,latitude,longitude,original_zip',
        'where': 'applieddate IS NOT NULL AND location IS NOT NULL',
        'order': 'project_id DESC',
        'limit': 1000000000,
    }

    try:
        permits = client.get(dataset_id, **query)
    except requests.exceptions.ConnectionError:
        event = 'Unable to establish connection to dataset server'
        log.error(event, exc_info=True)
        return 1
    except requests.exceptions.HTTPError:
        event = 'Received an error HTTP response from dataset server'
        log.error(event, exc_info=True)
        return 1
    except requests.exceptions.Timeout:
        event = 'Query to dataset timed out'
        log.error(event, exc_info=True)
        return 1
    except requests.exceptions.RequestException as e:
        event = 'Received unexpected error when fetching dataset'
        log.error(event, exc_info=True)
        return 1

    for permit in permits:
        log.info('Permit entry', **permit)

    log.info('Total number of permits', count=len(permits))

    return 0


if __name__ == '__main__':
    setup_logging()
    return_code = main()
    sys.exit(return_code)
