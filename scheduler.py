#!/usr/bin/env python3
"""
Scheduler for AI News Scraper
Runs the pipeline at configured times using APScheduler
"""

import logging
import sys
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from main import AINewsPipeline
from config import TIMEZONE_CONFIG, LOGGING_CONFIG

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format'],
    datefmt=LOGGING_CONFIG['date_format'],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG['log_file']),
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger(__name__)


class NewsScraperScheduler:
    """Scheduler for automated news scraping"""

    def __init__(self):
        """Initialize scheduler with configuration"""
        self.timezone = pytz.timezone(TIMEZONE_CONFIG['posting_timezone'])
        self.post_hours = TIMEZONE_CONFIG['post_hours']
        self.skip_weekends = TIMEZONE_CONFIG['skip_weekends']

        # Create scheduler
        self.scheduler = BlockingScheduler(timezone=self.timezone)

        # Setup jobs
        self._setup_jobs()

        logger.info("="*60)
        logger.info("AI NEWS SCRAPER SCHEDULER")
        logger.info("="*60)
        logger.info(f"Timezone: {TIMEZONE_CONFIG['posting_timezone']}")
        logger.info(f"Post hours: {self.post_hours}")
        logger.info(f"Skip weekends: {self.skip_weekends}")
        logger.info("="*60)

    def _setup_jobs(self):
        """Setup scheduled jobs"""
        # Schedule job for each post hour
        for hour in self.post_hours:
            # Determine day of week filter
            day_of_week = 'mon-fri' if self.skip_weekends else 'mon-sun'

            # Create cron trigger
            trigger = CronTrigger(
                hour=hour,
                minute=0,
                day_of_week=day_of_week,
                timezone=self.timezone
            )

            # Add job
            self.scheduler.add_job(
                self.run_pipeline,
                trigger=trigger,
                id=f'scraper_{hour:02d}00',
                name=f'AI News Scraper - {hour:02d}:00',
                max_instances=1,  # Prevent overlapping runs
                coalesce=True,  # If multiple missed, run only once
            )

            logger.info(f"✅ Scheduled job: Daily at {hour:02d}:00 {TIMEZONE_CONFIG['posting_timezone']}")

    def run_pipeline(self):
        """Run the news pipeline"""
        logger.info("")
        logger.info("🔔 SCHEDULED RUN TRIGGERED")
        logger.info(f"Time: {datetime.now(self.timezone)}")
        logger.info("")

        try:
            pipeline = AINewsPipeline()
            results = pipeline.run()

            if results['success']:
                logger.info("✅ Scheduled run completed successfully")
            else:
                logger.warning("⚠️  Scheduled run completed with issues")

        except Exception as e:
            logger.error(f"❌ Scheduled run failed: {e}", exc_info=True)

    def start(self):
        """Start the scheduler"""
        logger.info("")
        logger.info("🚀 Starting scheduler...")
        logger.info("")

        # Print next run times
        jobs = self.scheduler.get_jobs()
        logger.info("Next scheduled runs:")
        for job in jobs:
            next_run = job.next_run_time
            logger.info(f"  - {job.name}: {next_run}")

        logger.info("")
        logger.info("Press Ctrl+C to stop")
        logger.info("="*60)
        logger.info("")

        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("")
            logger.info("⚠️  Scheduler stopped by user")
            self.stop()

    def stop(self):
        """Stop the scheduler"""
        logger.info("Shutting down scheduler...")
        self.scheduler.shutdown(wait=False)
        logger.info("✅ Scheduler stopped")

    def run_now(self):
        """Run the pipeline immediately (for testing)"""
        logger.info("🧪 MANUAL RUN")
        self.run_pipeline()


def main():
    """Main entry point"""
    try:
        scheduler = NewsScraperScheduler()

        # Check for command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == '--now':
                # Run immediately and exit
                scheduler.run_now()
                sys.exit(0)
            elif sys.argv[1] == '--test':
                # Test API connections
                logger.info("Testing API connections...")
                pipeline = AINewsPipeline()
                success = pipeline.test_apis()
                sys.exit(0 if success else 1)
            elif sys.argv[1] == '--help':
                print("""
AI News Scraper Scheduler

Usage:
    python scheduler.py              Start scheduler (runs at configured times)
    python scheduler.py --now        Run pipeline immediately
    python scheduler.py --test       Test API connections
    python scheduler.py --help       Show this help message

Configuration:
    Edit config.py to change:
    - Posting times (TIMEZONE_CONFIG['post_hours'])
    - Timezone (TIMEZONE_CONFIG['posting_timezone'])
    - Weekend scheduling (TIMEZONE_CONFIG['skip_weekends'])

The scheduler will run the AI news pipeline at configured times.
Logs are saved to: {log_file}

Press Ctrl+C to stop the scheduler.
""".format(log_file=LOGGING_CONFIG['log_file']))
                sys.exit(0)
            else:
                logger.error(f"Unknown argument: {sys.argv[1]}")
                logger.error("Use --help to see available options")
                sys.exit(1)

        # Start scheduler
        scheduler.start()

    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
