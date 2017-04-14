# -*- coding: utf-8 -*-


import datetime
import logging
import os
import sys

import pymongo
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

    domain = os.environ['DOMAIN']
    app_token = os.environ['APP_TOKEN']
    dataset_id = os.environ['DATASET_ID']
    database_url = os.environ['DATABASE_URI']

    mongo_client = pymongo.MongoClient(database_url)
    client = sodapy.Socrata(domain, app_token)

    log.debug('Fetching count of dataset records')

    count = count_dataset(client, dataset_id)
    if count == None:
        log.error('Unable to query count of dataset')
        return 1

    log.info('Record count', count=count)

    db = mongo_client.permits
    index = db.all_permits

    log.debug('Fetching permits')

    for permit_set in fetch_permits(client, dataset_id, count):
        if permit_set == None:
            event = ('Excessive failures while fetching Socrata data, '
                     'exiting early')
            log.error(event)
            return 1

        log.debug('Cleaning permit set')

        permit_set = [clean_permit(permit) for permit in permit_set]

        try:
            result = index.insert_many(permit_set, ordered=False)
            insert_count = len(result.inserted_ids)
        except pymongo.errors.BulkWriteError as e:
            event = ('Error while bulk inserting data, '
                     'remaining documents will still be inserted')
            log.error(event, exc_info=True)
            insert_count = e.details.get('nInserted')
        finally:
            log.debug('bulk inserted permit data', count=insert_count)

    log.info('Finished fetching permits')

    log.debug('Total records in index table', count=index.count())

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


def fetch_permits(client, dataset_id, permit_count, limit=25_000):
    """Fetches permit records from dataset"""
    log = structlog.get_logger()

    # Set up for paginating through dataset
    pages = permit_count // limit
    # Handle remainder
    if permit_count % limit != 0:
        pages = pages + 1

    log.debug('Pages to fetch', pages=pages)

    for page in range(pages):
        query = {
            'select': '*',
            'where': 'issue_date IS NOT NULL',
            'order': 'issue_date DESC',
            'limit': limit,
            'offset': page * limit
        }

        log.info('Fetching page, will retry until success', page=page)

        # Retry multiple times or return null
        success = False
        data = None
        for attempt in range(10):
            log.info('attempt to fetch page', attempt=attempt+1)

            try:
                data = client.get(dataset_id, **query)
                success = True
            except requests.exceptions.ConnectionError:
                event = 'Unable to establish connection to dataset server'
                log.error(event, exc_info=True)
                continue
            except requests.exceptions.HTTPError:
                event = 'Received an error HTTP response from dataset server'
                log.error(event, exc_info=True)
                continue
            except requests.exceptions.Timeout:
                event = 'Query to dataset timed out'
                log.error(event, exc_info=True)
                continue
            except requests.exceptions.RequestException:
                event = 'Received unexpected error when fetching dataset'
                log.error(event, exc_info=True)
                continue

            # Break out early if data is fetched
            if success:
                break

        yield data

def clean_permit(permit):
    """Converts Socrata data into MongoDB format"""
    issue_date = datetime.datetime.strptime(permit['issue_date'],
                                            '%Y-%m-%dT%H:%M:%S.%f')

    permit['issue_date'] = issue_date

    return permit


if __name__ == '__main__':
    setup_logging()
    return_code = main()
    sys.exit(return_code)
