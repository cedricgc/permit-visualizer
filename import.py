# -*- coding: utf-8 -*-


import itertools
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

    log.debug('Fetching count of dataset records')

    count = count_dataset(client, dataset_id)
    if count == None:
        log.error('Unable to query count of dataset')
        return 1

    log.info('Record count', count=count)

    log.debug('Fetching permits')

    permits = fetch_permits(client, dataset_id, count)
    if permits == None:
        log.error('Unable to fetch permit records')
        return 1

    for permit in permits:
        log.info('Permit entry', **permit)

    return 0


def count_dataset(client, dataset_id):
    """Fetches the current number of permits in the dataset"""
    log = structlog.get_logger()

    query = {
        'select': 'count(*)'
    }

    try:
        count_query = client.get(dataset_id, **query)
    except requests.exceptions.ConnectionError:
        event = 'Unable to establish connection to dataset server'
        log.error(event, exc_info=True)
        return None
    except requests.exceptions.HTTPError:
        event = 'Received an error HTTP response from dataset server'
        log.error(event, exc_info=True)
        return None
    except requests.exceptions.Timeout:
        event = 'Query to dataset timed out'
        log.error(event, exc_info=True)
        return None
    except requests.exceptions.RequestException:
        event = 'Received unexpected error when fetching dataset'
        log.error(event, exc_info=True)
        return None

    log.info('count query response', response=count_query)

    # count will be in count field of first object
    count = int(count_query[0]['count'])

    return count


def fetch_permits(client, dataset_id, permit_count):
    """Fetches permit records from dataset"""
    log = structlog.get_logger()

    # Set up for paginating through dataset
    permits = []
    limit = 10_000
    pages = permit_count // limit
    # Handle remainder
    if permit_count % limit != 0:
        pages = pages + 1

    log.debug('Pages to fetch', pages=pages)

    for page in range(pages):
        query = {
            'select': '*',
            'where': 'applieddate IS NOT NULL',
            'order': 'applieddate DESC',
            'limit': limit,
            'offset': page * limit
        }

        try:
            data = client.get(dataset_id, **query)
        except requests.exceptions.ConnectionError:
            event = 'Unable to establish connection to dataset server'
            log.error(event, exc_info=True)
            return None
        except requests.exceptions.HTTPError:
            event = 'Received an error HTTP response from dataset server'
            log.error(event, exc_info=True)
            return None
        except requests.exceptions.Timeout:
            event = 'Query to dataset timed out'
            log.error(event, exc_info=True)
            return None
        except requests.exceptions.RequestException:
            event = 'Received unexpected error when fetching dataset'
            log.error(event, exc_info=True)
            return None

        permits.append(data)

    # Flatten to single iterator
    permits = itertools.chain.from_iterable(permits)

    return permits


if __name__ == '__main__':
    setup_logging()
    return_code = main()
    sys.exit(return_code)
