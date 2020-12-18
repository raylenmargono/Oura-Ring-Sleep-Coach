import logging
from typing import Any, List, Dict, Tuple

import arrow
import requests
import psycopg2

import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

API = 'https://api.ouraring.com'
READINESS_API = f'{API}/v1/readiness'
SLEEP_API = f'{API}/v1/sleep'
ACTIVITY_API = f'{API}/v1/activity'


def dump(
    cursor: Any,
    model: str,
    records: List[Dict],
):
    """Dump records into the corresponding table."""
    logger.info('Dumping into table %s', model)
    updated = 0
    created = 0
    for record in records:
        columns_parsed = (f'{key} = %s' for key in record.keys())
        set_line = ', '.join(columns_parsed)
        values = [*record.values(), record['summary_date']]
        sql = f'UPDATE {model} SET {set_line} WHERE summary_date = %s'
        logger.info(
            'EXECUTING %s: WITH VALUES %s',
            sql,
            values,
        )
        cursor.execute(sql, values)
        updated += cursor.rowcount
        if cursor.rowcount:
            continue

        columns = ', '.join(record.keys())
        value_params = ', '.join(['%s'] * len(record.keys()))
        sql = f'INSERT INTO {model} ({columns}) VALUES ({value_params})'
        logger.info(
            'EXECUTING %s: WITH VALUES %s',
            sql,
            list(record.values()),
        )
        cursor.execute(sql, list(record.values()))
        created += 1

    logger.info('Updated rows %s', updated)
    logger.info('Created rows %s', created)

def run():
    """Ingests Oura ring data into the database."""
    request_kwargs = {
        'headers': {
            'Authorization': f'Bearer {settings.OURA_PERSONAL_TOKEN}'
        },
        'params': {
            'start': '2019-01-01',
            'end': arrow.now().format('YYYY-MM-DD'),
        }
    }
    readiness_r = requests.get(READINESS_API, **request_kwargs)
    readiness_r.raise_for_status()
    readiness_data = readiness_r.json()['readiness']
    logger.info('Obtained readiness data: %s points', len(readiness_data))
    sleep_r = requests.get(SLEEP_API, **request_kwargs)
    sleep_r.raise_for_status()
    sleep_data = sleep_r.json()['sleep']
    logger.info('Obtained sleep data: %s points', len(sleep_data))
    activity_r = requests.get(ACTIVITY_API, **request_kwargs)
    activity_r.raise_for_status()
    activity_data = activity_r.json()['activity']
    logger.info('Obtained activity data: %s points', len(activity_data))


    with psycopg2.connect(**settings.DB_SETTINGS) as connection:
        with connection.cursor() as cursor:
            dump(cursor, 'readiness_data', readiness_data)
            dump(cursor, 'activity_data', activity_data)
            dump(cursor, 'sleep_data', sleep_data)

if __name__ == '__main__':
    run()
