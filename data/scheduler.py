from apscheduler.schedulers import blocking

import ingest
import sleep_coach_predict

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def _run():
    """Run the ingest and prediction functions."""
    logger.info('Running scheduled job now to ingest data')

    ingest.run()
    sleep_coach_predict.run()

    logger.info('Finish running scheduled job')

def run():
    """Run scheduler and run data fetching to power dashboard."""
    s = blocking.BlockingScheduler()
    s.add_job(_run, 'interval', minutes=10)
    s.start()

if __name__ == '__main__':
    run()

