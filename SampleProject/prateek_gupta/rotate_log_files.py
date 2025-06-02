import os
from datetime import datetime

from django.core.management.base import BaseCommand

from prateek_gupta.LogManager import get_log_files_details, logger
from util import log_error

# To run the command rotate_log_files once in every 30 days, add the following line
# in the crontab(crontab -e)
# 0 0 * * * /usr/bin/python3 /home/ubuntu/Portfolio/manage.py rotate_log_files --days_gap 30


class Command(BaseCommand):
    help = ('Command to rotate log files after number of days passed --days_gap argument'
            'or by default 30 days')

    def add_arguments(self, parser):
        parser.add_argument('--days_gap', default=30, type=int)

    def handle(self, *args, **options):
        logger.info("Log files rotation begins")
        # noinspection PyBroadException
        try:
            days_gap_for_file_rotation = options["days_gap"]
            log_files = get_log_files_details()
            if len(log_files) > 0:
                # Sorting dates and looping them
                for key in sorted(list(log_files.keys()),
                                  key=lambda x: datetime.strptime(x, '%Y-%m-%d')):
                    log_file_date = datetime.strptime(key, "%Y-%m-%d").date()
                    if ((datetime.now().date() - log_file_date).days >=
                            days_gap_for_file_rotation):
                        for file_name in log_files.get(key):
                            if os.path.exists(file_path + file_name):
                                os.remove(file_path + file_name)

                        del log_files[key]
                        logger.info("Deleted log files dated : "+key)
                    else:
                        break
        except Exception:
            logger.error("Error while rotating the log files")
            log_error()

        logger.info("Log files rotation ends")
