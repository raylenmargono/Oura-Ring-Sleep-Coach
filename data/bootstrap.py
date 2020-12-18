import psycopg2
import settings

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def create_tables():
    """Create migration table for app and inital models."""
    logger.info('Start bootstrapping')
    commands = (
        '''CREATE TABLE events (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            event_datetime TIMESTAMP
        )
        ''',
        '''CREATE TABLE sleep_coach (
            id SERIAL PRIMARY KEY,
            prediction_date VARCHAR(255),
            total_sleep_obtained INT,
            total_sleep_predicted INT,
            readiness_level VARCHAR(255)
        )
        ''',
        '''CREATE TABLE sleep_data (
            id SERIAL PRIMARY KEY,
            period_id INT,
            is_longest INT,
            timezone INT,
            bedtime_start TIMESTAMP,
            bedtime_end TIMESTAMP,
            summary_date DATE,
            score_total INT,
            score INT,
            total INT,
            score_disturbances INT,
            score_efficiency INT,
            score_latency INT,
            score_rem INT,
            score_deep INT,
            score_alignment INT,
            duration INT,
            awake INT,
            light INT,
            rem INT,
            deep INT,
            onset_latency INT,
            restless INT,
            efficiency INT,
            midpoint_time INT,
            hr_lowest INT,
            hr_average REAL,
            rmssd INT,
            breath_average INT,
            hypnogram_5min TEXT,
            midpoint_at_delta INT,
            hr_5min INT[],
            rmssd_5min INT[],
            bedtime_end_delta INT,
            bedtime_start_delta INT,
            temperature_delta REAL,
            temperature_deviation REAL,
            temperature_trend_deviation REAL
        )
        ''',
        '''CREATE TABLE readiness_data (
            id SERIAL PRIMARY KEY,
            summary_date DATE,
            period_id INT,
            score INT,
            score_previous_night INT,
            score_sleep_balance INT,
            score_previous_day INT,
            score_activity_balance INT,
            score_resting_hr INT,
            score_hrv_balance INT,
            score_recovery_index INT,
            score_temperature INT
        )
        ''',
        '''CREATE TABLE activity_data (
            id SERIAL PRIMARY KEY,
            summary_date DATE,
            day_start TIMESTAMP,
            day_end TIMESTAMP,
            timezone INT,
            score INT,
            score_stay_active INT,
            score_move_every_hour INT,
            target_calories REAL,
            target_km INT,
            target_miles REAL,
            total INT,
            to_target_miles INT,
            activity_timezone INT,
            to_target_km REAL,
            score_meet_daily_targets INT,
            score_training_frequency INT,
            score_training_volume INT,
            score_recovery_time INT,
            daily_movement INT,
            non_wear INT,
            rest INT,
            inactive INT,
            inactivity_alerts INT,
            low INT,
            medium INT,
            high INT,
            steps INT,
            cal_total INT,
            cal_active INT,
            met_min_inactive INT,
            met_min_low INT,
            met_min_medium_plus INT,
            met_min_medium INT,
            met_min_high INT,
            average_met REAL,
            class_5min TEXT,
            met_1min REAL[]
        )
        ''',
    )
    with psycopg2.connect(**settings.DB_SETTINGS) as conn:
        with conn.cursor() as cur:
            # create table one by one
            for command in commands:
                logger.info('EXECUTING: %s', command)
                cur.execute(command)
            # close communication with the PostgreSQL database server
            cur.close()
        # commit the changes
        conn.commit()
    logger.info('Complete bootstrap')

if __name__ == '__main__':
    create_tables()
