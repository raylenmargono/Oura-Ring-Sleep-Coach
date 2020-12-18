import arrow
import pandas as pd
import psycopg2
from psycopg2 import extras
from statsmodels.regression import linear_model as lm

import logging
import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


sql = '''
    SELECT
    readiness_data.summary_date,
    sleep_data.total,
    activity_data.cal_total,
    readiness_data.score,
    CASE WHEN events.name IS NOT NULL THEN true ELSE false END alcohol FROM readiness_data
    JOIN sleep_data ON sleep_data.summary_date = readiness_data.summary_date
    RIGHT JOIN activity_data ON activity_data.summary_date = readiness_data.summary_date
    LEFT JOIN events ON events.event_datetime::DATE = readiness_data.summary_date
    WHERE events.name = 'ALCOHOL' OR events.name is null
    ORDER BY summary_date
'''



def run():
    """Predict sleep time."""
    logger.info('Running prediction')
    model = lm.OLSResults.load('../prediction_model.pickle')
    with psycopg2.connect(**settings.DB_SETTINGS) as c:
        with c.cursor(cursor_factory = extras.RealDictCursor) as cursor:
            cursor.execute(sql)
            results = cursor.fetchall()

            data = pd.DataFrame(results)
            data['prev_day_readiness_score'] = data['score'].shift(1)
            predictions = (
                pd.DataFrame([data.iloc[-1].to_dict()])
                [['cal_total', 'prev_day_readiness_score', 'alcohol']]
            )
            predictions_df = predictions.append([predictions] * 2, ignore_index=True)
            predictions_df['score'] = (100, 85, 70)

            predictions_df['predictions'] = model.predict(predictions_df)
            predictions_df['performance'] = ('PEAK', 'GET_BY', 'EASY')

            logger.info('PREDICTION:\n%s', predictions_df)

            prediction_records = predictions_df.to_dict('record')
            cursor.execute(
                'DELETE FROM sleep_coach WHERE prediction_date::DATE = %s',
                (arrow.now().date(),)
            )
            for record in prediction_records:
                cursor.execute(
                    'INSERT INTO sleep_coach'
                    '(prediction_date, total_sleep_obtained, total_sleep_predicted, readiness_level)'
                    'VALUES (%s, %s, %s, %s)',
                (arrow.now().date(), 0, record['predictions'], record['performance'])
            )
            logger.info('Finish running prediction')

if __name__ == '__main__':
    run()
