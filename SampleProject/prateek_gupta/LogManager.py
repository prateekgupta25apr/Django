import logging
import os
import re
import shutil
import sys
from datetime import datetime

from prateek_gupta import project_dir, console_logs

main_log_folder_name = "logs/"
main_log_file_name = "logs.log"
max_file_size = 1024 * 1024 * 10  # 10MB


class LogFileLogger:
    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        file_path = os.path.join(project_dir, main_log_folder_name)

        if console_logs:
            handler = logging.StreamHandler(sys.stdout)
        else:
            handler = LogFileHandler(file_path)

        handler.setFormatter(logging.Formatter(
            fmt="%(asctime)s.%(msecs)03d %(funcName)s(){%(filename)s} : %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
        self.logger.addHandler(handler)


def get_log_files_details():
    log_files = dict()
    # Regular expression pattern to match the desired file names
    pattern = re.compile(r'^logs\.(\d{4}-\d{2}-\d{2})\.\d+\.log$')

    # Get list of all files in the directory
    all_files = os.listdir(project_dir + main_log_folder_name)

    # Filter files that match the specified pattern
    target_files = [file for file in all_files if pattern.match(file)]

    # Creating a dict with date as key and list of name of logfiles as value
    for file in target_files:
        date = pattern.match(file).group(1)
        filenames = log_files.get(date, list())
        filenames.append(file)
        log_files[date] = filenames

    return log_files


class LogFileHandler(logging.FileHandler):
    def __init__(self, file_path, filemode="a"):
        filename = os.path.join(file_path, main_log_file_name)
        self.file_path = file_path
        self.main_log_file = filename
        self.last_log_file_date = "1999-04-25"
        self.log_file_next_serial_number = 1

        # Getting log files details as dict
        log_files = get_log_files_details()

        # Initializing last_log_file_date and log_file_next_serial_number
        if len(log_files.keys()) > 0:
            # As the self.log_files will be ordered according to dates in ascending order
            # so getting last date
            self.last_log_file_date = list(log_files.keys())[-1]

            # Plus one to track next log file serial number
            self.log_file_next_serial_number = (
                    len(log_files[self.last_log_file_date]) + 1)

        super().__init__(filename, mode=filemode)

    def handle(self, record):
        if os.path.getsize(self.main_log_file) > max_file_size:
            # noinspection PyBroadException
            try:
                self.close()

                shutil.copy(self.main_log_file, self.file_path + self.get_log_file_name())

                self.last_log_file_date = datetime.now().strftime("%Y-%m-%d")
                self.log_file_next_serial_number += 1

                # noinspection PyTypeChecker
                self.stream = open(self.main_log_file, "w")
            except Exception:
                print("Error occurred while printing logs")
        return super().handle(record)

    def get_log_file_name(self):
        log_file_date = datetime.strptime(self.last_log_file_date, "%Y-%m-%d").date()
        if (datetime.now().date() - log_file_date).days >= 1:
            self.log_file_next_serial_number = 1

        return ("logs." + datetime.now().strftime("%Y-%m-%d") + "." +
                str(self.log_file_next_serial_number) + ".log")


logger = LogFileLogger().logger


def rotate_log_files(days_gap_for_file_rotation=30):
    logger.info("Log files rotation begins")
    # noinspection PyBroadException
    try:
        log_files = get_log_files_details()
        file_path = os.path.join(project_dir, main_log_folder_name)
        if len(log_files) > 0:
            # Sorting dates and looping them
            for key in sorted(list(log_files.keys()),
                              key=lambda x: datetime.strptime(x, '%Y-%m-%d')):
                log_file_date = datetime.strptime(key, "%Y-%m-%d").date()
                if ((datetime.now().date() - log_file_date).days >=
                        int(days_gap_for_file_rotation)):
                    for file_name in log_files.get(key):
                        if os.path.exists(file_path + file_name):
                            os.remove(file_path + file_name)

                    del log_files[key]
                    logger.info("Deleted log files dated : " + key)
                else:
                    break
    except Exception as e:
        logger.error("Error while rotating the log files")
        from prateek_gupta.exceptions import log_error
        log_error()
        raise e

    logger.info("Log files rotation ends")
